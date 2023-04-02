from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import pandas as pd
import numpy as np
import time

fake = UserAgent().random
print(fake)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument(f'user-agent={fake}')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument('--disable-logging')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})

apartments = pd.DataFrame()

def scraper(query_enter: str, driver: webdriver.Chrome):
    global apartments
    name = query_enter

    elements = driver.find_elements(
        By.XPATH, '//ul[@class="Ul-sctud2-0 jyGHXP realestate-results-list browse-results-list"]/li')
    
    for i in elements:
        try:
            price = i.find_element(
                By.XPATH, './/div[@class="card-block"]/ul/li[1]/p').text

            price = price[1:].replace('.', '')

            area = i.find_element(
                By.XPATH, './/div[@class="card-block"]/ul/li[2]/p').text

            area = float(area[:-3])

            habitaciones = i.find_element(
                By.XPATH, './/div[@class="card-block"]/ul/li[3]/p').text

            baños = i.find_element(
                By.XPATH, './/div[@class="card-block"]/ul/li[4]/p').text

            link = i.find_element(
                By.XPATH, './/div[@class="card-header"]/a').get_attribute('href')

            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link)

            try:
                estrato = driver.find_element(
                    By.XPATH, './/div[@class="Col-sc-14ninbu-0 lfGZKA col-md-9"]/div[4]').text[-9]

                datos_principales = driver.find_elements(
                    By.XPATH, './/html/body/div[2]/div/div/div/div[2]/div[4]/div[1]/div[8]/div/div')

                if len(datos_principales) == 0:
                    datos_principales = driver.find_elements(
                        By.XPATH, './/html/body/div[2]/div/div/div/div[2]/div[4]/div[1]/div[7]/div/div')
                
                administracion = np.nan
                parqueadero = np.nan
                antiguead = np.nan
                barrio = np.nan
                codigo = np.nan

                for i in datos_principales:
                    try:
                        bloque_datos_titulo = i.find_element(
                            By.XPATH, './/h3')
                        
                        bloque_datos_texto = i.find_element(
                            By.XPATH, './/p')
                        
                        if 'Valor administración' in bloque_datos_titulo.text:
                            administracion = bloque_datos_texto.text
                            administracion = int(administracion[1:].replace('.', ''))

                        if 'Parqueaderos' in bloque_datos_titulo.text:
                            parqueadero = int(bloque_datos_texto.text)

                        if 'Antigüedad' in bloque_datos_titulo.text:
                            antiguead = bloque_datos_texto.text

                        if 'Barrio común' in bloque_datos_titulo.text:
                            barrio = bloque_datos_texto.text

                        if 'Código inmueble' in bloque_datos_titulo.text:
                            codigo = bloque_datos_texto.text

                    except Exception as e:
                        print('Error en datos_principales')
                        print(e)
                        pass
                
                try:
                    descripcion = driver.find_element(
                        By.XPATH, './/html/body/div[2]/div/div/div/div[2]/div[4]/div[1]/div[6]/p').text
                except:
                    descripcion = driver.find_element(
                        By.XPATH, './/html/body/div[2]/div/div/div/div[2]/div[4]/div[1]/div[5]/p').text

                interiores = driver.find_elements(
                    By.XPATH, '//div[@class="Card-sc-18qyd5o-0 jYfunq sc-kgAjT kgGRzv is-active card"]/div[2]/div/div/div')

                equipado = 0
                sauna = 0
                piso = np.nan
                jacuzzi = 0
                calefaccion = 0
                vista_exterior = 0
                for i in interiores:
                    try:
                        if 'amoblado' in i.text.lower():
                            equipado = 1

                        if 'Piso ' in i.text:
                            piso = i.text[-1]

                        if 'Sauna / turco' in i.text:
                            sauna = 1

                        if 'Jacuzzi' in i.text:
                            jacuzzi = 1

                        if 'Calefacción' in i.text:
                            calefaccion = 1

                        if 'Vista exterior' in i.text:
                            vista_exterior = 1

                    except Exception as e:
                        print('Error en interiores')
                        equipado = np.nan
                        piso = np.nan
                        pass
                
                exterior_btn = driver.find_element(
                    By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div[4]/div[1]/div[12]/div/div[2]')
                

                driver.execute_script("arguments[0].scrollIntoView();", exterior_btn)
                exterior_btn.click()

                exterior = driver.find_elements(
                    By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div[4]/div[1]/div[12]/div/div[2]/div[2]/div/div/div')
                
                porteria = 0
                vista_panoramica = 0
                picina = 0
                terraza = 0
                balcon = 0
                area_terraza_balcon = np.nan
                for i in exterior:
                    if 'Piscina' in i.text:
                        picina = 1

                    if 'Area Terraza/Balcón' in i.text:
                        area_terraza_balcon = i.text
                        area_terraza_balcon = area_terraza_balcon[20:].strip()
                        area_terraza_balcon = float(area_terraza_balcon[:-3])

                    if 'Portería' in i.text:
                        porteria = 1

                    if 'Vista panorámica' in i.text:
                        vista_panoramica = 1

                    if 'Terraza/Balcón terraza' in i.text:
                        terraza = 1

                    if 'Terraza/Balcón balcón' in i.text:
                        balcon = 1

                    if 'Con terraza' in i.text:
                        terraza = 1
                
            except:
                print('Error en el proceso')
                pass

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            data = {
                'precio': price,
                'area_m2': area,
                'habitaciones': habitaciones,
                'baños': baños,
                'estrato': estrato,
                'barrio': barrio,
                'antiguead': antiguead,
                'administracion': administracion,
                'parqueadero': parqueadero,
                'piso': piso,
                'codigo': codigo,
                'equipado': equipado,
                'sauna': sauna,
                'jacuzzi': jacuzzi,
                'calefaccion': calefaccion,
                'porteria': porteria,
                'vista_panoramica': vista_panoramica,
                'vista_exterior': vista_exterior,
                'picina': picina,
                'terraza': terraza,
                'balcon': balcon,
                'area_terraza_balcon_m2': area_terraza_balcon,
                'descripcion': descripcion,
                'link': link,
                'query': name,
                'date': time.ctime()
            }

            df_temp = pd.DataFrame(data, index=[0])
            apartments = pd.concat([apartments, df_temp], ignore_index=True)

            print('--------------------------------------')
            print(len(apartments))
            for i in data:
                print(i, ':', data[i])
            print('--------------------------------------\n')
        except Exception as e:
            pass

def run(name: str, path: str = None):
    url = f'https://www.metrocuadrado.com/apartamento/venta/bogota/{name}/'

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    while True:
        try:
            scraper(name, driver)
            next_page = driver.find_element(
                By.XPATH, '//li[@class="item-icon-next page-item"]/a')
            driver.execute_script("arguments[0].click();", next_page)
            print('next page')
            time.sleep(2)
        except Exception as e:
            print('no more pages')
            driver.close()
            break

    apartments.to_csv(f'{path}{name}_m2.csv', index=False)

if __name__ == '__main__':
    run('chapinero')