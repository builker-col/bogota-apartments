import requests

# url = "https://www.dropbox.com/scl/fi/bxj03wii0ez50ixe9q5yv/builker.scrapy_bogota_apartmentsV1.2.0_august_1.json?rlkey=btg69ut2biha7xd1j5llk0gj4&dl=1" # V1.2.0 August 1
url = "https://www.dropbox.com/scl/fi/ar2d96q96c8vqxvrpyr9i/builker.scrapy_bogota_apartments.json?rlkey=w93hngjdaiosuhjcr1zsktomn&dl=1"

# Haga una solicitud GET a la URL
response = requests.get(url)

# Guarde el archivo JSON en el directorio de trabajo actual
with open("builker.scrapy_bogota_apartments.json", 'wb') as f:
    f.write(response.content)