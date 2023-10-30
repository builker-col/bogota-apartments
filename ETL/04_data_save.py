from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import pymongo
import logging
import os

load_dotenv()

filename = f'logs/04_data_save.log'
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename=filename)

if os.getcwd().split('/')[-1] == 'ETL':
    logging.info('Cambiando directorio de trabajo')
    os.chdir('..')

logging.info(f'Process started at {datetime.now()}')
# Connect to MongoDB
logging.info('Connecting to MongoDB')
client = pymongo.MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('MONGO_DATABASE')]
collection = db['scrapy_bogota_apartments_processed']

PREOCESSED_DATA = 'data/processed/apartments.csv'

# Read the processed data
logging.info('Reading the processed data')
try:
    df = pd.read_csv(PREOCESSED_DATA, low_memory=False)
    logging.info('Processed data read successfully')
except Exception as error:
    logging.error(error)
    exit(1)

# Save the processed data to MongoDB
logging.info('Saving the processed data to MongoDB')
# leer, buscar si existe, sie existe mirar si es igual, si es igual no hacer nada, si es diferente actualizar, si no existe insertar
try:
    for index, row in df.iterrows():
        apartment = collection.find_one({'codigo': row['codigo']})
        if apartment is None:
            collection.insert_one(row.to_dict())
        else:
            if apartment != row.to_dict():
                collection.update_one({'codigo': row['codigo']}, {'$set': row.to_dict()})

    logging.info('Processed data saved successfully')

except Exception as error:
    logging.error(error)
    exit(1)

# Close the connection to MongoDB
logging.info('Closing the connection to MongoDB')
client.close()

logging.info(f'Process finished at {datetime.now()}')
