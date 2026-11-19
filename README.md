# Map geometry update

This project rebuilds the geometries (GeoJSON) of the geographical categories in `carte.json` from open data sources, then:

1. generates a `carte_update.json` file with the replaced geometries;
2. imports it into MongoDB (`geographicalcategories2`);

## Levels handled

| Level | Source | Function |
|---|---|---|
| `urbanUnity` | INSEE, 2020 urban unit boundaries | `get_uu()` |
| `department` | data.gouv.fr | `get_dep()` |
| `academy` | Union of each academy's departments (data.gouv.fr links) | `get_aca()` |
| `region` | data.gouv.fr (+ `R00` = overseas territories grouped together) | `get_reg()` |
| `country` | Natural Earth 1:10m | `get_pays()` |

Each function returns a dictionary `{originalId: GeoJSON}`.

## Project structure

```
├── carte.ipynb           # notebook: the steps, top to bottom
├── config.py             # URLs, constants, file names, Mongo / API settings
├── fonctions_geo.py      # geometry building (get_uu, get_dep, get_aca, get_reg, get_pays)
├── fonctions_export.py   # replacement, MongoDB import, Paysage structures
├── requirements.txt
├── carte.json            # (to provide) original map
└── .env                  # (to create) 
```

## Installation

```bash
pip install -r requirements.txt
```

Additional requirement for the MongoDB import: the **`mongoimport`** tool (MongoDB Database Tools). Its path is set in `config.py` (`MONGOIMPORT`).

## Configuration

Create a `.env` file at the project root:

```
MONGO_URL=`mongodb url`
API_key_paysage=your_api_key
```

## Usage

Open `carte.ipynb` and run the cells in order:

 | Content |
|---|
 | Imports and loading of `carte.json` |
 | Urban units |
 | Departments |
 | Academies (depends on step 2) |
 | Regions |
 | Countries |
 | Geometry replacement → writes `carte_update.json` |
 | MongoDB import |

After each building step, a check cell (`ids_manquants`) lists the identifiers from `carte.json` that have no new geometry. #An empty list means everything is covered.#

### Process a single level only

At step 6, replace the full merge with the level you want:

```python
dict_all = dict_uu   # instead of dict_world | dict_uu | dict_dep | dict_aca | dict_reg
```

## Things to watch

- **Sources**: the URLs of the boundary files (INSEE, data.gouv.fr) contain the vintage year. Update them in `config.py` with each new release.
