# useful for handling different item types with a single interface
from bogota_apartments.items import ApartmentsItem
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
from datetime import datetime
import logging
import pymongo
import json

class MongoDBPipeline(object):
    collection = get_project_settings().get('MONGO_COLLECTION_RAW')

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.logger.info(f'Connected to MongoDB: {self.mongo_uri}/{self.mongo_db}')

    def close_spider(self, spider):
        self.client.close()
        self.logger.info('Closed MongoDB connection')

    def process_item(self, item, spider):
        data = dict(ApartmentsItem(item))

        if spider.name == 'metrocuadrado':
            existing_item = self.db[self.collection].find_one({'codigo': data['codigo']})
            self.logger.info(f'Processing item with codigo: {data["codigo"]}')

            data['caracteristicas'] = []
            for key in ['featured_interior', 'featured_exterior', 'featured_zona_comun', 'featured_sector']:
                if key in data:
                    data['caracteristicas'] += data[key]
                    del data[key]

            if existing_item:
                self.logger.info(f'Updating existing item with codigo: {data["codigo"]}')
                existing_item['last_view'] = datetime.now()

                if 'timeline' not in existing_item:
                    existing_item['timeline'] = []

                try:
                    fields = ['precio_venta', 'precio_arriendo']
                    
                    for field in fields:
                        if field in data and field in existing_item and data[field] != existing_item[field]:
                            if len(existing_item['timeline']) == 0:
                                existing_item['timeline'].append({
                                    'fecha': existing_item['datetime'],
                                    field: existing_item[field],
                                })

                            existing_item['timeline'].append({
                                'fecha': datetime.now(),
                                field: data[field],
                            })
                            
                            existing_item[field] = data[field]
                except KeyError:
                    self.logger.error('Error al actualizar el item: %s', data['codigo'])
                    pass
                
                self.db[self.collection].update_one({'codigo': data['codigo']}, {'$set': existing_item})
            else:
                self.logger.info(f'Inserting new item with codigo: {data["codigo"]}')
                self.db[self.collection].insert_one(data)

            return item

        elif spider.name == 'habi':
            existing_item = self.db[self.collection].find_one({'codigo': data['codigo']})
            if existing_item:
                self.logger.info(f'Updating existing item with codigo: {data["codigo"]}')
                existing_item['last_view'] = datetime.now()
                
                if 'timeline' not in existing_item:
                    existing_item['timeline'] = []

                try:
                    if data['precio_venta'] != existing_item['precio_venta']:
                        if len(existing_item['timeline']) == 0:
                            existing_item['timeline'].append({
                                'fecha': existing_item['datetime'],
                                'precio_venta': existing_item['precio_venta'],
                            })

                        existing_item['timeline'].append({
                            'fecha': datetime.now(),
                            'precio_venta': data['precio_venta'],
                        })
                        
                        existing_item['precio_venta'] = data['precio_venta']
                except KeyError:
                    pass

                self.db[self.collection].update_one({'codigo': data['codigo']}, {'$set': existing_item})
            else:
                self.logger.info(f'Inserting new item with codigo: {data["codigo"]}')
                self.db[self.collection].insert_one(data)

            return item
            
        self.db[self.collection].insert_one(data)
        self.logger.info(f'Inserting new item with codigo: {data["codigo"]}')
        return item

class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item