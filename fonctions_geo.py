import io
import re
import json
import zipfile
from collections import Counter

import requests
import pandas as pd
import geopandas as gpd
import shapely

from config import (
    UU_URL, UU_HEADERS, DEP_URL, ACA_DEP_URL, REG_URL, REG_OUTRE_MER,
    WORLD_URL, WORLD_COLS, LIST_MISSING,
)

#Conversion en geommetry shape valide
def to_geom(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, shapely.geometry.base.BaseGeometry):
        return v
    if isinstance(v, str):
        return shapely.from_wkt(v)
    if isinstance(v, (bytes, bytearray)):
        return shapely.from_wkb(v)
    if isinstance(v, dict):                      
        return shapely.from_geojson(json.dumps(v))
    if hasattr(v, "geometry"):                   
        return shapely.union_all(list(v.geometry))
    return None

#Réparation des géométries invalides
def to_valid(g):
    if g is None:
        return None
    return g if shapely.is_valid(g) else shapely.make_valid(g)


#garde que les polygones
def only_polygons(g):
    if g is None or g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    polys = [p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")]
    return shapely.union_all(polys) if polys else None


#Union des départements d'une académie
def join_geojson(x, aca_dep, dict_dep_geom):
    geoms = [dict_dep_geom[d] for d in aca_dep.get(x, [])
             if dict_dep_geom.get(d) is not None]
    if not geoms:
        return None
    try:
        return shapely.union_all(geoms)
    except shapely.errors.GEOSException:
        return shapely.union_all(geoms, grid_size=1e-6)


#Vérification : identifiants de la carte sans géométrie pour un niveau
def ids_manquants(df, level, dict_geom):
    return [x for x in list(df[df.level == level].originalId) if x not in list(dict_geom.keys())]


#Unités urbaines
def get_uu():
    contenu = requests.get(UU_URL, headers=UU_HEADERS, timeout=180).content

    with zipfile.ZipFile(io.BytesIO(contenu)) as z:
        nom = [n for n in z.namelist() if n.endswith("uu2020_2026.zip") and "com_" not in n][0]
        zip_uu = z.read(nom)

    uu = gpd.read_file(io.BytesIO(zip_uu))
    uu = pd.DataFrame(uu.drop(columns='geometry')).assign(geometry=list(uu.geometry))
    uu = uu.rename(columns={'uu2020': 'originalId', 'geometry': 'geometry_uu'})
    uu.loc[:, 'geometry_uu'] = uu.loc[:, 'geometry_uu'].apply(lambda g: json.loads(shapely.to_geojson(g)))

    dict_uu = dict(zip(uu['originalId'], uu['geometry_uu']))
    return dict_uu


#Départements
def get_dep():
    dep = gpd.read_file(DEP_URL)
    dep['originalId'] = dep.code.apply(lambda x: str('D' + x.zfill(3)))
    dep.loc[:, 'geometry_dep'] = dep.loc[:, 'geometry'].apply(lambda g: json.loads(shapely.to_geojson(g)))

    dict_dep = dict(zip(dep['originalId'], dep['geometry_dep']))
    return dict_dep


#Académies
def get_aca(df, dict_dep):
    aca_dep = pd.read_json(ACA_DEP_URL)

    aca_dep['dep_id'] = aca_dep.fields.apply(lambda x: x['dep_id'])
    aca_dep['aca_id'] = aca_dep.fields.apply(lambda x: x['aca_id'])

    aca_dep = aca_dep[['aca_id', 'dep_id']].drop_duplicates()
    aca_dep = pd.DataFrame(aca_dep.groupby('aca_id')['dep_id'].apply(list)).reset_index()
    aca_dep = dict(zip(aca_dep['aca_id'], aca_dep['dep_id']))

    aca = df[df.level == 'academy'][['originalId', 'geometry']]

    # dictionnaire des départements en "geometry" valide
    dict_dep_geom = {k: only_polygons(to_valid(to_geom(v))) for k, v in dict_dep.items()}

    # jointures des départements en académies
    aca['geometry'] = aca['originalId'].apply(lambda x: join_geojson(x, aca_dep, dict_dep_geom))

    # geojson au meme format que l'ancien 
    aca['geometry_aca'] = aca['geometry'].apply(
        lambda g: json.loads(shapely.to_geojson(g)) if g is not None else None
    )

    print(Counter(type(v).__name__ for v in dict_dep_geom.values()))
    print("Clés manquantes :", {d for deps in aca_dep.values() for d in deps if d not in dict_dep_geom})
    print("Académies sans géométrie :", aca.loc[aca['geometry'].isna(), 'originalId'].tolist())

    dict_aca = dict(zip(aca['originalId'], aca['geometry_aca']))
    return dict_aca


#Régions
def get_reg():
    reg = gpd.read_file(REG_URL)
    reg['code'] = reg.code.apply(lambda x: str('R' + x))

    gdf = reg[reg.code.apply(lambda x: x in REG_OUTRE_MER)].copy()
    gdf['geometry_reg'] = gdf.geometry.make_valid()

    reg = pd.concat([reg, gpd.GeoDataFrame({'code': ['R00']}, geometry=[gdf.geometry_reg.union_all()])], ignore_index=True)
    reg.loc[:, 'geometry_reg'] = reg.loc[:, 'geometry'].apply(lambda g: json.loads(shapely.to_geojson(g)))

    dict_reg = dict(zip(reg['code'], reg['geometry_reg']))
    return dict_reg


#Pays
def get_pays(df):
    world = gpd.read_file(WORLD_URL)

    world = pd.DataFrame(world)
    world.loc[:, 'geometry_country'] = world.loc[:, 'geometry'].apply(lambda g: json.loads(shapely.to_geojson(g)))
    df = df[df.level == 'country']
    geometry_missing = world[world['ADM0_A3'].apply(lambda x: x in LIST_MISSING)]

    world2 = pd.concat([world[WORLD_COLS + ['geometry_country']], geometry_missing])

    cols = [c for c in WORLD_COLS if c in world2.columns]

    valid = re.compile(r'[A-Z]{3}')

    dict_world = {}
    for c in cols:
        for code, geom in zip(world2[c], world2.geometry_country):
            if isinstance(code, str) and valid.fullmatch(code):
                dict_world.setdefault(code, geom)

    missing = set(df['originalId']) - set(dict_world)
    print("Pays sans géométrie :", missing)

    return dict_world