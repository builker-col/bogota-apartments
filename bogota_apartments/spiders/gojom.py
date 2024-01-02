from bogota_apartments.items import ApartmentsItem
from scrapy.loader import ItemLoader
from datetime import datetime
import scrapy
import re


class GojomSpider(scrapy.Spider):
    name = "gojom"
    allowed_domains = ["gojom.co"]
    start_urls = ["https://gojom.co/compra/apartamento/bogota?page=1"]

    def parse(self, response):
        apartments = response.xpath('//div[@id="item-list"]/div')

        for apartment in apartments:
            try:
                codigo = apartment.xpath('./@id').get().split('-')[-1]
                url = apartment.xpath('.//a/@href').get()
                if url:
                    print(codigo, url)
                    yield response.follow(url, callback=self.parse_detail, meta={'codigo': codigo})
            except:
                pass

        # next_page = response.xpath('//ul[@class="pagination justify-content-center"]/li[last()]/a/@href').get()
        # if next_page:
            # yield response.follow(next_page, callback=self.parse)

    def parse_detail(self, response):
        loader = ItemLoader(item=ApartmentsItem(), response=response)
        loader.add_value('codigo', response.meta['codigo'])

        # tipo de propiedad
        loader.add_xpath('tipo_propiedad', '//div[@class="box property-item my-1"]/div[2]/div[2]/p[2]/text()')
        # tipo de operacion
        loader.add_xpath('tipo_operacion', '//div[@class="box property-item my-1"]/div[2]/div[1]/p[2]/text()')
        # precio de venta
        precio_venta = response.xpath('//div[@class="x-small local-price-segment text-left"]/span[2]/text()').get()
        loader.add_value('precio_venta', precio_venta.replace('.', ''))
        # area
        area = response.xpath('//div[@class="box property-item my-1"]/div[3]/div[1]/p[2]/text()').get()
        loader.add_value('area', area.replace('m²', ''))
        # habitaciones
        loader.add_xpath('habitaciones', '//div[@class="box property-item my-1"]/div[3]/div[3]/p[2]/text()')
        # banos
        loader.add_xpath('banos', '//div[@class="box property-item my-1"]/div[3]/div[4]/p[2]/text()')
        # administracion
        administracion = response.xpath('/html/body/div[5]/div[1]/div[7]/div[2]/div[1]/div/div[3]/div/div[3]/span[2]/span[2]/text()').get(), 
        if isinstance(administracion, str):
            loader.add_value('administracion', administracion.replace('.', ''))
        elif isinstance(administracion, tuple):
            if administracion[0]:
                loader.add_value('administracion', administracion[0].replace('.', ''))
        # parqueaderos
        loader.add_xpath('parqueaderos', '//div[@class="box property-item my-1"]/div[3]/div[5]/p[2]/text()')
        # sector
        loader.add_xpath('sector', '//*[@id="show-content-title"]/div[1]/div/p/text()')
        # estrato
        estrato = response.xpath('//*[@id="show-content-title"]/div[1]/div/span/text()').get()        
        loader.add_value('estrato', estrato.replace('Estrato ', ''))
        # estado
        loader.add_xpath('estado', '/html/body/div[5]/div[1]/div[7]/div[1]/div/div/div[1]/div/div[2]/div[4]/p[2]/text()')
        # antiguedad
        antiguedad = response.xpath('/html/body/div[5]/div[1]/div[7]/div[1]/div/div/div[1]/div/div[2]/div[3]/p[2]/text()').get()
        loader.add_value('antiguedad', antiguedad.replace(' años', ''))
        # latitud y longitud
        pattern = r"markers=([-+]?\d+\.\d+),([-+]?\d+\.\d+)"
        mapa = response.xpath('//*[@id="gmap_static"]/@src').get()
        # print('\n\n\n')
        # print(mapa)
        # print('\n\n\n')
        # latitud = re.search(pattern, mapa).group(1)
        # longitud = re.search(pattern, mapa).group(2)

        # loader.add_value('latitud', latitud)
        # loader.add_value('longitud', longitud)
        # # caracteristicas
        caracteristicas = response.xpath('/html/body/div[5]/div[1]/div[7]/div[1]/div/div/div[1]/div/div[4]/div')
        caracteristicas_list = []
        for caracteristica in caracteristicas:
            caracteristicas_list.append(caracteristica.xpath('./span/span/text()').get())
        loader.add_value('caracteristicas', caracteristicas_list)

        # descripcion
        loader.add_xpath('descripcion', '/html/body/div[5]/div[1]/div[7]/div[1]/div/div/div[1]/div/p[3]/text()')

        #TODO: imagenes
        # website
        loader.add_value('website', 'gojom.co')
        # last_view
        loader.add_value('last_view', datetime.now())
        # datetime 
        loader.add_value('datetime', datetime.now())
        # url
        loader.add_value('url', response.url)

        yield loader.load_item()