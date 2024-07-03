# Author: Erik Garcia (@erik172)
# Version: Unreleased
from datetime import datetime
import subprocess
import logging

filename = f'logs/data_pipeline.log'

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename=filename)

def run_data_pipeline():
    logging.info(f'Start data pipeline at {datetime.now()}')

    logging.info('Start web scraping HABI')
    subprocess.run(['scrapy', 'crawl', 'habi'])
    logging.info('Start web scraping METROCUADRADO')
    subprocess.run(['scrapy', 'crawl', 'metrocuadrado'])
    logging.info('End web scraping')

    logging.info('Start data processing')
    subprocess.run(['python3.11', 'ETL/01_initial_transformations.py'])
    subprocess.run(['python3.11', 'ETL/02_data_correction.py'])
    subprocess.run(['python3.11', 'ETL/03_data_enrichment.py'])    
    logging.info('End data processing')

    logging.info('Start data saving')
    subprocess.run(['python3.11', 'ETL/04_data_save.py'])
    logging.info('End data saving')

    logging.info(f'End data pipeline at {datetime.now()}')

if __name__ == '__main__':
    run_data_pipeline()
