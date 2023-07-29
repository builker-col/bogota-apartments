import requests

# Obtenga la URL del archivo JSON
url = "https://www.dropbox.com/s/1ly47276dnqqdzp/builker.scrapy_bogota_apartments.json?dl=1"

# Haga una solicitud GET a la URL
response = requests.get(url)

# Guarde el archivo JSON en el directorio de trabajo actual
with open("builker.scrapy_bogota_apartments.json", 'wb') as f:
    f.write(response.content)