from src import extract_features
from dotenv import load_dotenv
import logging
import pandas as pd
import pymongo
import os

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# verificar si etoy dentro de la carpeta notebooks o no
if os.getcwd().split('/')[-1] == 'notebooks':
    os.chdir('..')

# Connect to MongoDB
logging.info('Connecting to MongoDB')

try:
    client = pymongo.MongoClient(os.getenv('MONGO_URI'))
    db = client[os.getenv('MONGO_DATABASE')]
    collection = db['scrapy_bogota_apartments']
    logging.info('Connected to MongoDB')

except pymongo.errors.ConnectionFailure as error:
    logging.error(error)
    exit(1)

# Get data from MongoDB
df = pd.DataFrame(list(collection.find()))
df = df.drop(columns=['_id'], axis=1)

# Transformations
logging.info('Transforming data (explode images)')
images_explode = df.explode('imagenes')
images_explode = images_explode.dropna(subset=['imagenes'])

images_df = images_explode[['codigo', 'imagenes']].rename(columns={'imagenes': 'url_imagen'})
images_df.to_csv('data/processed/images.csv', index=False)
logging.info(f'Images saved, shape: {images_df.shape}')

df = df.drop(columns=['imagenes'], axis=1)

logging.info('Transforming data (extract features)')
df['jacuzzi'] = df.featured_interior.apply(extract_features.check_jacuzzi)
df['piso'] = df.featured_interior.apply(extract_features.extract_piso)
df['closets'] = df.featured_interior.apply(extract_features.extract_closets)
df['chimenea'] = df.featured_interior.apply(extract_features.check_chimeny)
df['permite_mascotas'] = df.featured_interior.apply(extract_features.check_mascotas)
df['gimnasio'] = df.featured_zona_comun.apply(extract_features.check_gimnasio)
df['ascensor'] = df.featured_exterior.apply(extract_features.check_ascensor)
df['conjunto_cerrado'] = df.featured_exterior.apply(extract_features.check_conjunto_cerrado)

df = df.drop(columns=['featured_interior', 'featured_zona_comun', 'featured_exterior', 'featured_sector'], axis=1)

df.to_csv('data/interim/apartments.csv', index=False)
logging.info(f'Data saved, shape: {df.shape}')