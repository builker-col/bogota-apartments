import requests

# Obtenga la URL del archivo JSON
# url = "https://www.dropbox.com/s/1ly47276dnqqdzp/builker.scrapy_bogota_apartments.json?dl=1"
url = "https://www.dropbox.com/scl/fi/bxj03wii0ez50ixe9q5yv/builker.scrapy_bogota_apartments.json?rlkey=btg69ut2biha7xd1j5llk0gj4&dl=1"

# Haga una solicitud GET a la URL
response = requests.get(url)

# Guarde el archivo JSON en el directorio de trabajo actual
with open("builker.scrapy_bogota_apartments.json", 'wb') as f:
    f.write(response.content)