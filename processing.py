#!/usr/bin/python3.11
from datetime import datetime
import subprocess
import logging

filename = f'logs/data_processing.log'

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename=filename)

def run_data_processing():
    """
    Runs the data processing pipeline.

    This function executes a series of data processing steps, including initial transformations,
    data correction, data enrichment, and data saving. It logs the start and end times of the
    pipeline execution.

    """
    logging.info(f'Start data pipeline at {datetime.now()}')

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
    run_data_processing()