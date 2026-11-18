#Fichiers
FICHIER_CARTE = './carte.json'
FICHIER_CARTE_UPDATE = 'carte_update.json'

#Unités urbaines (INSEE)
UU_URL = "https://www.insee.fr/fr/statistiques/fichier/4802589/fonds_uu2020_2026.zip"
UU_HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.insee.fr/"}

#Départements
DEP_URL = 'https://contours-administratifs.s3.rbx.io.cloud.ovh.net/2026/geojson/departements-100m.geojson'

#Académies (liens académie-départements)
ACA_DEP_URL = 'https://www.data.gouv.fr/api/1/datasets/r/a1475d8d-e4a4-48a6-8287-f79d21c57904'

#Régions
REG_URL = 'https://www.data.gouv.fr/api/1/datasets/r/225bbf1f-13c4-4913-bd8a-55c2f28e0149'
REG_OUTRE_MER = ['R986', 'R988', 'R987', 'R989', 'R975', 'R977', 'R978', 'R984']  # regroupées dans R00

#Pays
WORLD_URL = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_0_countries.zip"
WORLD_COLS = ['ADM0_A3', 'ISO_A3', 'ISO_A3_EH', 'BRK_A3', 'GU_A3', 'SU_A3', 'SOV_A3']
LIST_MISSING = ['GIB', 'NRU', 'CYM', 'CPV', 'BRB', 'GRD', 'SGP', 'SXM', 'FSM', 'DMA', 'IMN', 'MUS', 'TUV', 'HKG', 'KIR', 'MLT', 'GUM', 'MAC', 'FRO', 'KNA', 'ASM', 'TCA', 'BMU', 'GIB', 'SMR', 'MAF', 'VCT', 'MNP', 'CUW', 'BHR', 'ATG', 'VGB', 'VAT', 'COM', 'AND', 'MCO', 'SYC', 'MDV', 'MHL', 'LIE', 'TON', 'STP', 'WSM', 'PLW', 'ABW', 'LCA']

#MongoDB
MONGOIMPORT = r"C:\Program Files\MongoDB\Tools\100\bin\mongoimport.exe"
MONGO_DB = "paysage-staging"
MONGO_COLLECTION = "geographicalcategories2"

#API Paysage
PAYSAGE_URL_PROD = "https://api.paysage.dataesr.ovh/structures"
PAYSAGE_URL_STAGING = "https://paysage-api.staging.dataesr.ovh/structures"