# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from bogota_apartments.items import ApartmentsItem
from scrapy.exceptions import DropItem
from datetime import datetime
import pymongo

class MongoDBPipeline(object):
    collection = 'scrapy_bogota_apartments'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # start with a clean database
        # self.db[self.collection].delete_many({})

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        data = dict(ApartmentsItem(item))

        if spider.name == 'metrocuadrado':
            existing_item = self.db[self.collection].find_one({'codigo': data['codigo']})

            if existing_item:
                # Comprueba y actualiza los campos opcionales si es necesario
                if 'imagenes' not in existing_item:
                    existing_item['imagenes'] = data.get('imagenes')

                if 'compañia' not in existing_item:
                    existing_item['compañia'] = data.get('compañia')

                if data['precio_venta'] == existing_item['precio_venta'] and data['precio_arriendo'] == existing_item['precio_arriendo']:
                    raise DropItem("Ya existe el item, precio de venta y arriendo igual")
                else:
                    # Actualiza el precio de venta si ha cambiado
                    if data['precio_venta'] != existing_item['precio_venta']:
                        existing_item['precio_venta_anterior'] = existing_item['precio_venta']
                        existing_item['fecha_actualizacion_precio_venta'] = datetime.now()

                    # Actualiza el precio de arriendo si ha cambiado
                    if data['precio_arriendo'] != existing_item['precio_arriendo']:
                        existing_item['precio_arriendo_anterior'] = existing_item['precio_arriendo']
                        existing_item['fecha_actualizacion_precio_arriendo'] = datetime.now()

                    # Actualiza el item en la base de datos
                    self.db[self.collection].update_one({'codigo': data['codigo']}, {'$set': existing_item})
            else:
                # Inserta el item en la base de datos si no existe
                self.db[self.collection].insert_one(data)

            return item

        # Si el spider no es 'metrocuadrado', inserta el item directamente en la base de datos
        self.db[self.collection].insert_one(data)
        return item
