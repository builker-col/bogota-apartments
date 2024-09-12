from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import pymongo
import logging
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configurar el registro de eventos
filename = 'logs/04_data_save.log'
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename=filename)

# Cambiar el directorio de trabajo si es necesario
if os.path.basename(os.getcwd()) == 'ETL':
    logging.info('Changing working directory')
    os.chdir('..')

# Iniciar el proceso y registrar el inicio
logging.info(f'Process started at {datetime.now()}')

try:
    # Conectar a MongoDB
    logging.info('Connecting to MongoDB')
    client = pymongo.MongoClient(os.getenv('MONGO_URI'))
    db = client[os.getenv('MONGO_DATABASE')]
    collection = db['scrapy_bogota_apartments_processed']

    # Ruta al archivo de datos procesados
    PROCESSED_DATA = 'data/processed/apartments.csv'

    # Leer los datos procesados desde el archivo CSV
    logging.info('Reading the processed data')
    df = pd.read_csv(PROCESSED_DATA, low_memory=False)
    logging.info('Processed data read successfully')

    # Guardar los datos procesados en MongoDB
    logging.info('Saving the processed data to MongoDB')
    for index, row in df.iterrows():
        apartment = collection.find_one({'codigo': row['codigo']})
        if apartment:
            if apartment != row.to_dict():
                collection.update_one({'codigo': row['codigo']}, {'$set': row.to_dict()})
        else:
            collection.insert_one(row.to_dict())

    logging.info('Processed data saved successfully')

except FileNotFoundError as e:
    logging.error(f'File not found: {e}')

except pd.errors.EmptyDataError as e:
    logging.error(f'Empty data error: {e}')

except Exception as e:
    logging.error(f'An error occurred: {e}')

finally:
    # Cerrar la conexión a MongoDB
    if 'client' in locals():
        logging.info('Closing the connection to MongoDB')
        client.close()

    logging.info(f'Process finished at {datetime.now()}')

