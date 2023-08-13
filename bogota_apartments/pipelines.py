"""
This module defines the pipelines for the bogota_apartments Scrapy project. It contains a MongoDBPipeline class that
handles the processing of items and their storage in a MongoDB database.

Classes:
    MongoDBPipeline: A class that handles the processing of items and their storage in a MongoDB database.
"""

# useful for handling different item types with a single interface
from bogota_apartments.items import ApartmentsItem
from scrapy.exceptions import DropItem
from datetime import datetime
import pymongo

class MongoDBPipeline(object):
    """
    A class that handles the processing of items and their storage in a MongoDB database.

    Attributes:
        collection (str): The name of the collection in the MongoDB database.
        mongo_uri (str): The URI of the MongoDB instance.
        mongo_db (str): The name of the MongoDB database.

    Methods:
        from_crawler(cls, crawler): Returns an instance of the class with the specified URI and database name.
        open_spider(self, spider): Initializes the MongoDB client and database.
        close_spider(self, spider): Closes the MongoDB client.
        process_item(self, item, spider): Processes the item and stores it in the MongoDB database.
    """

    collection = 'scrapy_bogota_apartments'

    def __init__(self, mongo_uri, mongo_db):
        """
        Initializes a new instance of the MongoDBPipeline class.

        Args:
            mongo_uri (str): The URI of the MongoDB instance.
            mongo_db (str): The name of the MongoDB database.
        """
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        """
        Returns an instance of the class with the specified URI and database name.

        Args:
            crawler (scrapy.crawler.Crawler): The Scrapy crawler.

        Returns:
            MongoDBPipeline: An instance of the MongoDBPipeline class.
        """
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        """
        Initializes the MongoDB client and database.

        Args:
            spider (scrapy.Spider): The Scrapy spider.
        """
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # start with a clean database
        # self.db[self.collection].delete_many({})

    def close_spider(self, spider):
        """
        Closes the MongoDB client.

        Args:
            spider (scrapy.Spider): The Scrapy spider.
        """
        self.client.close()

    def process_item(self, item, spider):
        """
        Processes the item and stores it in the MongoDB database.

        Args:
            item (scrapy.Item): The Scrapy item.
            spider (scrapy.Spider): The Scrapy spider.

        Returns:
            scrapy.Item: The processed Scrapy item.
        """
        data = dict(ApartmentsItem(item))

        if spider.name == 'metrocuadrado':
            existing_item = self.db[self.collection].find_one({'codigo': data['codigo']})

            if existing_item:
                # Comprueba y actualiza los campos opcionales si es necesario
                if 'imagenes' not in existing_item:
                    existing_item['imagenes'] = data.get('imagenes')

                if 'compañia' not in existing_item:
                    existing_item['compañia'] = data.get('compañia')

                try:
                    # Actualiza el precio de venta si ha cambiado
                    if data['precio_venta'] != existing_item['precio_venta']:
                        existing_item['precio_venta_anterior'] = existing_item['precio_venta']
                        existing_item['precio_venta'] = data['precio_venta']
                        existing_item['fecha_actualizacion_precio_venta'] = datetime.now()

                except KeyError:
                    pass

                try:
                    # Actualiza el precio de arriendo si ha cambiado
                    if data['precio_arriendo'] != existing_item['precio_arriendo']:
                        existing_item['precio_arriendo_anterior'] = existing_item['precio_arriendo']
                        existing_item['precio_arriendo'] = data['precio_arriendo']
                        existing_item['fecha_actualizacion_precio_arriendo'] = datetime.now()
                except KeyError:
                    pass

                # Actualiza el item en la base de datos
                self.db[self.collection].update_one({'codigo': data['codigo']}, {'$set': existing_item})

            else:
                # Inserta el item en la base de datos si no existe
                self.db[self.collection].insert_one(data)

            return item

        elif spider.name == 'habi':
            if self.db[self.collection].find_one({'codigo': data['codigo']}):
                raise DropItem(f'Item {data["codigo"]} already exists in MongoDB')
            
        self.db[self.collection].insert_one(data)
        return item
