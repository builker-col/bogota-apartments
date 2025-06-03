"""
This module defines the pipelines for the bogota_apartments Scrapy project. It contains a MongoDBPipeline class that
handles the processing of items and their storage in a MongoDB database.

Classes:
    MongoDBPipeline: A class that handles the processing of items and their storage in a MongoDB database.
"""

# useful for handling different item types with a single interface
from bogota_apartments.items import ApartmentsItem
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
from datetime import datetime
import logging
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

    collection = get_project_settings().get('MONGO_COLLECTION_RAW')

    def __init__(self, mongo_uri, mongo_db):
        """
        Initializes a new instance of the MongoDBPipeline class.

        Args:
            mongo_uri (str): The URI of the MongoDB instance.
            mongo_db (str): The name of the MongoDB database.
        """
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.logger = logging.getLogger(__name__)

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
            # Buscar apartamento existente solo por codigo
            existing_item = self.db[self.collection].find_one({'codigo': data['codigo']})
            
            data['caracteristicas'] = []
            for key in ['featured_interior', 'featured_exterior', 'featured_zona_comun', 'featured_sector']:
                if key in data:
                    data['caracteristicas'] += data[key]
                    del data[key]

            if existing_item:
                existing_item['last_view'] = datetime.now()

                if 'timeline' not in existing_item:
                    existing_item['timeline'] = []

                try:
                    fields = ['precio_venta', 'precio_arriendo']
                    
                    # 🔄 Centralizar manejo del timeline - combinar cambios en una sola entrada
                    price_changes = {}
                    has_changes = False
                    
                    for field in fields:
                        if field in data and field in existing_item and data[field] != existing_item[field]:
                            price_changes[field] = {
                                'old': existing_item[field],
                                'new': data[field]
                            }
                            existing_item[field] = data[field]
                            has_changes = True
                    
                    # Solo crear entradas del timeline si hay cambios de precio
                    if has_changes:
                        # Si el timeline está vacío, agregar entrada inicial con precios originales
                        if len(existing_item['timeline']) == 0:
                            initial_entry = {'fecha': existing_item['datetime']}
                            for field in fields:
                                if field in price_changes:
                                    initial_entry[field] = price_changes[field]['old']
                            existing_item['timeline'].append(initial_entry)
                        
                        # Agregar nueva entrada con precios actualizados (combinados)
                        new_entry = {'fecha': datetime.now()}
                        for field, change in price_changes.items():
                            new_entry[field] = change['new']
                        
                        existing_item['timeline'].append(new_entry)
                        
                        # Log para debugging
                        changes_str = ', '.join([f'{field}: ${change["old"]:,} → ${change["new"]:,}' 
                                               for field, change in price_changes.items()])
                        self.logger.info(f'💰 Timeline actualizado para {data["codigo"]}: {changes_str}')
                        
                except KeyError:
                    self.logger.error('Error al actualizar el item: %s', data['codigo'])
                    pass
                
                # Actualiza el item en la base de datos usando solo codigo
                self.db[self.collection].update_one({'codigo': data['codigo']}, {'$set': existing_item})

            else:
                # Inserta el item en la base de datos si no existe
                self.db[self.collection].insert_one(data)

            return item

        elif spider.name == 'habi':
            existing_item = self.db[self.collection].find_one({'codigo': data['codigo']})
            if existing_item:
                existing_item['last_view'] = datetime.now()
                
                if 'timeline' not in existing_item:
                    existing_item['timeline'] = []

                try:
                    # 🔄 Centralizar manejo del timeline para Habi también
                    if 'precio_venta' in data and data['precio_venta'] != existing_item['precio_venta']:
                        # Si el timeline está vacío, agregar entrada inicial con precio original
                        if len(existing_item['timeline']) == 0:
                            existing_item['timeline'].append({
                                'fecha': existing_item['datetime'],
                                'precio_venta': existing_item['precio_venta'],
                            })

                        # Agregar nueva entrada con precio actualizado
                        existing_item['timeline'].append({
                            'fecha': datetime.now(),
                            'precio_venta': data['precio_venta'],
                        })
                        
                        # Log para debugging
                        self.logger.info(f'💰 Timeline actualizado para Habi {data["codigo"]}: ${existing_item["precio_venta"]:,} → ${data["precio_venta"]:,}')
                        
                        existing_item['precio_venta'] = data['precio_venta']
                except KeyError:
                    pass

                self.db[self.collection].update_one({'codigo': data['codigo']}, {'$set': existing_item})

            else:
                # Inserta el item en la base de datos si no existe
                self.db[self.collection].insert_one(data)

            return item
        
        elif spider.name == 'metrocuadrado_search':
            return item
            
        self.db[self.collection].insert_one(data)
        return item