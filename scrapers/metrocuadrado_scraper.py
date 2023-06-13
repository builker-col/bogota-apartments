from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions as EX
from fake_useragent import UserAgent
from datetime import datetime
import pandas as pd
import logging
import yaml
import time
import re
import os

# Configuración de los logs del scraper
try:
    logging.basicConfig(filename='scrapers/logs/metrocuadrado.log', level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s', encoding='utf-8')
except:
    logging.basicConfig(filename='logs/metrocuadrado.log', level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s', encoding='utf-8', filemode='w')
    
handler = logging.StreamHandler()
logging.getLogger().addHandler(handler)

# Crear User Agent aleatorio para evitar ser bloqueado
fake = UserAgent().random
logging.debug(f'User agent: {fake}')

# Configuración de Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument(f'user-agent={fake}')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--log-level=2')
chrome_options.add_argument('--disable-logging')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})

# Crear DataFrame vacío para almacenar los datos de los apartamentos
apartments = pd.DataFrame()

# Cargar los xpaths del archivo yml
try:
    with open('xpaths.yml') as file:
        xpaths = yaml.safe_load(file)
except:
    with open('scrapers/xpaths.yml') as file:
        xpaths = yaml.safe_load(file)


class MetrocuadradoScraper:
    def __init__(self, query_enter: str, file_name: str = 'venta_apartamentos'):
        """Inicializa el scraper de metrocuadrado para la venta de apartamentos en Bogotá
        
        Args:
            query_enter (str): Barrio de Bogotá o Ciudad de Colombia
            file_name (str, optional): Nombre del archivo csv. Defaults to 'venta_apartamentos'.
        """
        self.query_enter = query_enter.lower()
        self.driver = webdriver.Chrome(options=chrome_options)
        self.df = pd.DataFrame()
        self.file_name = file_name
        self.images_file_name = f'{self.file_name}_imagenes'

        if self.query_enter == 'bogota':
            self.url = 'https://www.metrocuadrado.com/apartamentos/venta/bogota/'
        else:
            self.url = f'https://www.metrocuadrado.com/apartamentos/venta/bogota/{self.query_enter}/'

        # definirlo antes, ya que varia segun el tipo de apartamento
        self.precio = xpaths['metrocuadrado']['detalles_apartamento']['precio']

    def run(self):
        """Inicia el scraper"""
        logging.info(f'Iniciando scraper')
        self.driver.get(self.url)
        while True:
            try:
                self.scraper()
                next_page = self.driver.find_element(
                    By.XPATH, xpaths['metrocuadrado']['next_page']
                )
                self.driver.execute_script("arguments[0].click();", next_page)
                time.sleep(.5)
            except EX.NoSuchElementException:
                logging.warning('No more pages')
                break

            except KeyboardInterrupt:
                logging.exception('KeyboardInterrupt')
                break

            except Exception as e:
                logging.error(e)
        self.export_to_csv()        

    def new_window(self, link) -> None:
        """Abre una nueva ventana y se mueve a ella
        
        Args:
            link (str): link de la nueva ventana
            
        Returns:
            None"""
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(link)
        logging.info(f'New window: {self.driver.title}')

    def close_window(self) -> None:
        """Cierra la ventana actual y se mueve a la anterior"""
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        logging.debug(f'Close window: {self.driver.title}')

    def extract_details(self) -> dict:
        """Extrae los detalles del apartamento

        Returns:
            dict: Diccionario con los detalles del apartamento
        """
        try:
            # precio = self.driver.find_element(
            #     By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['precio']).text
            precio = self.driver.find_element(
                By.XPATH, self.precio).text
            precio = precio[1:].replace('.', '')
        except:
            precio = pd.NA

        try:
            habitaciones = self.driver.find_element(
                By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['habitaciones']).text
            # Eliminar el texto '\nHabitaciones'
            habitaciones = habitaciones[:-13]
        except:
            habitaciones = pd.NA

        try:
            baños = self.driver.find_element(
                By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['banos']).text
            # Eliminar el texto '\nBaños'
            baños = baños[:-6]
        except:
            baños = pd.NA

        try:
            estrato = self.driver.find_element(
                By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['estrato']).text
            # Eliminar el texto '\nEstrato'
            estrato = estrato[:-8]
        except:
            estrato = pd.NA

        try:
            sector = self.driver.find_element(
                By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['sector']).text
            
            sector = sector.split(',')[0]
            sector = sector.upper()
            if sector[:6] == 'SECTOR':
                sector = sector[7:]

        except:
            sector = pd.NA

        try:
            descripcion = self.driver.find_element(
                By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['descripcion']).text
        except:
            descripcion = pd.NA

        try:
            script = self.driver.find_element(
                By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['script_data']).get_attribute('innerHTML')

            # Expresión regular para extraer las coordenadas
            patron = r'"coordinates":{"lon":([-.\d]+),"lat":([-.\d]+)}'
            coord = re.search(patron, script)

            latitud = float(coord.group(2))
            longitud = float(coord.group(1))

            # Expresión regular para extraer las urls de las imágenes
            patron = r'"image":"(https?://[^"]+)"'
            urls_imagenes = re.findall(patron, script)

            images = pd.DataFrame(urls_imagenes, columns=['url'])

        except Exception as e:
            logging.error(e)
            latitud = pd.NA
            longitud = pd.NA
            images = pd.DataFrame()

        datos_principales = self.driver.find_elements(
            By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['datos_principales']
        )

        codigo = pd.NA
        barrio = pd.NA
        antiguedad = pd.NA
        area_construida = pd.NA
        area_privada = pd.NA
        valor_administracion = pd.NA
        parqueaderos = pd.NA

        for i in datos_principales:
            texto = i.find_element(
                By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['datos_principales_texto']
            ).text
            
            value = i.find_element(
                By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['datos_principales_value']
            ).text

            if 'Código inmueble' in texto:
                codigo = value

            if 'Barrio común' in texto:
                barrio = value.upper()

            if 'Antigüedad' in texto:
                antiguedad = value

            if 'Área construida' in texto:
                area_construida = value
                area_construida = area_construida.replace('m²', '')

            if 'Área privada' in texto:
                area_privada = value
                area_privada = area_privada.replace('m²', '')

            if 'Valor administración' in texto:
                valor_administracion = value
                valor_administracion = valor_administracion[1:].replace('.', '')

            if 'Parqueaderos' in texto:
                parqueaderos = value

        caracteristicas = self.driver.find_elements(
            By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['caracteristicas']
        )

        piso = pd.NA
        amoblado = 0
        sauna = 0
        jacuzzi = 0
        deposito = pd.NA
        vista_exterior = 0
        closets = pd.NA
        calefaccion = 0
        estufa = pd.NA
        vigilancia = 0
        numero_ascensores = pd.NA
        cerca_parque = 0
        cerca_transporte = 0
        cerca_centros_comerciales = 0
        cerca_colegios_universidades = 0
        cerca_supermercados = 0
        zona_residencial = pd.NA
        sobre_via_secundaria = 0
        sobre_via_principal = 0
        zc_zonas_verdes = 0
        zc_salon_comunal = 0
        zc_gimnasio = 0
        zc_zonas_bbq = 0
        zc_zonas_infantiles = 0
        zc_cancha_squash = 0
        vista_panoramica = 0
        acceso_discapacitados = 0
        terraza_balcon = pd.NA
        area_terraza_balcon = pd.NA
        terraza = 0
        parqueadero_visitantes = 0

        for i in caracteristicas:
            titulo = i.find_element(
                By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['caracteristicas_titulo']
            )

            if 'Interiores' in titulo.text:
                interiores = i.find_elements(
                    By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['caracteristicas_values']
                )

                for j in interiores:
                    try:
                        value = j.find_element(
                            By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['caracteristicas_value']
                        ).text

                        if 'Piso' in value and len(value) < 9:
                            piso = value
                            piso = piso.replace('Piso', '')

                        if 'Equipado / amoblado' in value:
                            amoblado = 1

                        if 'Sauna / turco' in value:
                            sauna = 1

                        if 'Jacuzzi' in value:
                            jacuzzi = 1

                        if 'Deposito' in value:
                            deposito = value
                            deposito = deposito.replace('Deposito', '')

                        if 'Vista exterior' in value:
                            vista_exterior = 1

                        if 'Closets' in value and len(value) < 11:
                            closets = value
                            closets = closets.replace('Closets', '')

                        if 'Calefacción' in value:
                            calefaccion = 1

                        if 'Tipo de estufa' in value:
                            estufa = value
                            estufa = estufa.replace('Tipo de estufa ', '')
                    except:
                        pass

            if 'Exteriores' in titulo.text:
                self.driver.execute_script("arguments[0].click();", titulo)

                exteriores = i.find_elements(
                    By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['caracteristicas_values']
                )

                for j in exteriores:
                    try:
                        value = j.find_element(
                            By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['caracteristicas_value']
                        ).text

                        if 'Vigilancia' in value:
                            vigilancia = 1

                        if 'Número de Ascensores' in value:
                            numero_ascensores = value
                            numero_ascensores = numero_ascensores.replace('Número de Ascensores ', '')

                        if 'Vista panorámica' in value:
                            vista_panoramica = 1

                        if 'Acceso para discapacitados' in value:
                            acceso_discapacitados = 1

                        if 'Terraza/Balcón' in value:
                            terraza_balcon = value
                            terraza_balcon = terraza_balcon.replace('Terraza/Balcón ', '')

                        if 'Area Terraza/Balcón' in value:
                            area_terraza_balcon = value
                            area_terraza_balcon = area_terraza_balcon.replace('Area Terraza/Balcón ', '')
                            area_terraza_balcon = area_terraza_balcon.replace('m²', '')

                        if 'Con terraza' in value:
                            terraza = 1

                        if 'Parqueadero visitantes' in value:
                            parqueadero_visitantes = 1
                    except:
                        pass

            if 'Del sector' in titulo.text:
                self.driver.execute_script("arguments[0].click();", titulo)

                del_sector = i.find_elements(
                    By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['caracteristicas_values']
                )

                for j in del_sector:
                    try:
                        value = j.find_element(
                            By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['caracteristicas_value']
                        ).text

                        if 'Cerca parques' in value:
                            cerca_parque = 1

                        if 'Cerca transporte público' in value:
                            cerca_transporte = 1

                        if 'Cerca centros comerciales' in value:
                            cerca_centros_comerciales = 1

                        if 'Cerca colegios / universidades' in value:
                            cerca_colegios_universidades = 1

                        if 'Cerca supermercados' in value:
                            cerca_supermercados = 1

                        if 'Zona residencial' in value:
                            zona_residencial = 1

                        if 'Sobre vía secundaria' in value:
                            sobre_via_secundaria = 1

                        if 'Sobre vía principal' in value:
                            sobre_via_principal = 1

                    except:
                        pass

            if 'Zonas comunes' in titulo.text:
                self.driver.execute_script("arguments[0].click();", titulo)

                zonas_comunes = i.find_elements(
                    By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['caracteristicas_values']
                )

                for j in zonas_comunes:
                    try:
                        value = j.find_element(
                            By.XPATH, xpaths['metrocuadrado']['detalles_apartamento']['caracteristicas_value']
                        ).text

                        if 'Zonas verdes' in value:
                            zc_zonas_verdes = 1

                        if 'Salón comunal' in value:
                            zc_salon_comunal = 1

                        if 'Gimnasio' in value:
                            zc_gimnasio = 1

                        if 'Zona de BBQ' in value:
                            zc_zonas_bbq = 1

                        if 'Zona para niños' in value:
                            zc_zonas_infantiles = 1

                        if 'Cancha(s) de squash' in value:
                            zc_cancha_squash = 1
                    except:
                        pass

        
        if len(images) > 0:
            images['codigo'] = codigo
            self.save_images(data=images)
            # logging.info('Images saved')

        return {
            'precio': precio,
            'habitaciones': habitaciones,
            'baños': baños,
            'estrato': estrato,
            'codigo': codigo,
            'barrio': barrio,
            'sector': sector,
            'antiguedad': antiguedad,
            'area_m2': area_construida,
            'administracion': valor_administracion,
            'parqueaderos': parqueaderos,
            'piso': piso,
            'amoblado': amoblado,
            'sauna': sauna,
            'jacuzzi': jacuzzi,
            'deposito': deposito,
            'vista_exterior': vista_exterior,
            'closets': closets,
            'calefaccion': calefaccion,
            'estufa': estufa,
            'vigilancia': vigilancia,
            'numero_ascensores': numero_ascensores,
            'cerca_parque': cerca_parque,
            'cerca_transporte': cerca_transporte,
            'cerca_centros_comerciales': cerca_centros_comerciales,
            'cerca_colegios_universidades': cerca_colegios_universidades,
            'cerca_supermercados': cerca_supermercados,
            'zona_residencial': zona_residencial,
            'sobre_via_secundaria': sobre_via_secundaria,
            'sobre_via_principal': sobre_via_principal,
            'zc_zonas_verdes': zc_zonas_verdes,
            'zc_salon_comunal': zc_salon_comunal,
            'zc_gimnasio': zc_gimnasio,
            'zc_zonas_bbq': zc_zonas_bbq,
            'zc_zonas_infantiles': zc_zonas_infantiles,
            'zc_cancha_squash': zc_cancha_squash,
            'acceso_discapacitados': acceso_discapacitados,
            'vista_panoramica': vista_panoramica,
            'terraza_balcon': terraza_balcon,
            'area_terraza_balcon': area_terraza_balcon,
            'terraza': terraza,
            'parqueadero_visitantes': parqueadero_visitantes,
            'latitud': latitud,
            'longitud': longitud,
            'descripcion': descripcion,
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'url': self.driver.current_url,
            'fuente': 'metrocuadrado',
            'query': self.query_enter,
        }
    
    def scraper(self, sleep_time: int = 1):
        """Scraper para metrocuadrado.com
        
        Args:
            sleep_time (int, optional): Tiempo de espera para cargar la página. Defaults to 1.
        """
        apartments = WebDriverWait(self.driver, sleep_time).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, xpaths['metrocuadrado']['apartamentos'])
            )
        )

        for i in apartments:
            url_to_apartment = i.find_element(
                By.XPATH, xpaths['metrocuadrado']['url_detalles_apartamento']).get_attribute('href')

            self.new_window(url_to_apartment)
            
            details = self.extract_details()

            self.close_window()

            df_temp = pd.DataFrame(details, index=[0])
            self.df = pd.concat([self.df, df_temp], ignore_index=True)
            df_temp = None

            # print(details)
            # print('\n\n')

    def save_images(self, data_path = 'data/raw/metrocuadrado', data: pd.DataFrame = None):
        """Guarda las imágenes de los apartamentos en un archivo csv
        
        Args:
            data_path (str, optional): Ruta donde se guardará el archivo csv. Defaults to 'data/raw/metrocuadrado'.
            data (pd.DataFrame, optional): Dataframe con los datos de las imágenes. Defaults to None.
        """
        # verifica si existe el archivo images.csv
        if os.path.isfile(f'{data_path}/{self.images_file_name}.csv'):
            # si existe, lo carga
            df_images = pd.read_csv(f'{data_path}/{self.images_file_name}.csv', index_col=False)
        else:
            # si no existe, crea un dataframe vacío
            df_images = pd.DataFrame(columns=['codigo', 'url'])

        df_images = pd.concat([df_images, data], ignore_index=True)
        df_images.to_csv(f'{data_path}/{self.images_file_name}.csv', index=False)

    
    def export_to_csv(self, data_path = 'data/raw/metrocuadrado'):
        """Exporta los datos a un archivo csv

        Args:
            data_path (str, optional): Ruta donde se guardará el archivo csv. Defaults to 'data/raw/metrocuadrado'.
        """
        self.df.to_csv(f'{data_path}/{self.file_name}.csv', index=False)
        logging.info(f'Archivo {self.file_name}.csv exportado correctamente. {self.df.shape[0]} registros')
        logging.info(f'Archivo en {data_path}/{self.file_name}.csv')

        logging.info(f'Imagenes guardadas en {data_path}/{self.images_file_name}.csv')


class MetrocuadradoArriendoScraper(MetrocuadradoScraper):
    def __init__(self, query_enter: str):
        """Scraper para metrocuadrado.com de arriendo de apartamentos
        
        Args:
            query_enter (str): Barrio o localidad y/o ciudad
        """
        super().__init__(query_enter)
        self.file_name = f'arriendo_apartamentos_{self.query_enter}'
        self.images_file_name = f'arriendo_apartamentos_imagenes_{self.query_enter}'
        if self.query_enter == 'bogota':
            self.url = 'https://www.metrocuadrado.com/apartamentos/arriendo/bogota/'
        else:
            self.url = f'https://www.metrocuadrado.com/apartamentos/arriendo/bogota/{self.query_enter}/'

        self.precio = './/div[@class="Col-sc-14ninbu-0 lfGZKA pl-0 d-none d-sm-inline-block col-md-9"]/div/h3'

if __name__ == '__main__':
    scraper = MetrocuadradoScraper('bosque-izquierdo')
    scraper.run()

    arriendo = MetrocuadradoArriendoScraper('bosque-izquierdo')
    arriendo.run()