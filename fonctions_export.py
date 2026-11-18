import os
import re
import json
import subprocess
 
import requests
from dotenv import load_dotenv
 
from config import (
    MONGOIMPORT, MONGO_DB, MONGO_COLLECTION,
    PAYSAGE_URL_PROD, PAYSAGE_URL_STAGING,
)
 
 
# Remplacer toutes les geometries
def replace(row, dict_all):
    if dict_all.get(row['originalId']) is not None:
        return dict_all[row['originalId']]
    else:
        return row['geometry']
 
 
def update_carte(df_all, dict_all):
    df_all.loc[:, 'geometry'] = df_all.apply(lambda row: replace(row, dict_all), axis=1)
    return df_all
 
 
def save_dict(d, fichier):
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(d, f)
 
 
#dump MongoDB
def dump_mongo(fichier):
    load_dotenv()
 
    u = os.getenv("MONGO_URL")
    if not u:
        raise SystemExit("MONGO_URL n'est pas dans le .env")
 
    base, db, query = re.match(r"^(mongodb(?:\+srv)?://[^/?]+)/?([^?]*)\??(.*)$", u.strip()).groups()
    if db and "authSource" not in query:
        query = "&".join(x for x in [query, f"authSource={db}"] if x)
 
    r = subprocess.run(
        [
            MONGOIMPORT,
            f"--uri={base}/?{query}",
            f"--db={MONGO_DB}",
            f"--collection={MONGO_COLLECTION}",
            f"--file={fichier}",
            "--jsonArray",
        ],
        capture_output=True, text=True,
    )
    print(r.returncode)
    print(r.stdout)
    print(r.stderr.replace(u, "***"))