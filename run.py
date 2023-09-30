import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_data_pipeline():
    """
    Runs the data pipeline for web scraping and data processing.

    This function runs two subprocesses to execute Scrapy spiders for web scraping and three subprocesses to execute
    Python scripts for data processing. The web scraping subprocesses execute the 'habi' and 'metrocuadrado' spiders
    respectively. The data processing subprocesses execute the '01_initial_transformations.py', '02_data_correction.py',
    and '03_data_enrichment.py' scripts respectively.

    Returns:
        None
    """
    logging.info('Start web scraping')
    subprocess.run(['scrapy', 'crawl', 'habi'])
    subprocess.run(['scrapy', 'crawl', 'metrocuadrado'])
    logging.info('End web scraping')

    logging.info('Start data processing')
    subprocess.run(['python3', 'notebooks/01_initial_transformations.py'])
    subprocess.run(['python3', 'notebooks/02_data_correction.py'])
    subprocess.run(['python3', 'notebooks/03_data_enrichment.py'])    
    logging.info('End data processing')

if __name__ == '__main__':
    run_data_pipeline()