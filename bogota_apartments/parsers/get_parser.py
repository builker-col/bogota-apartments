from bogota_apartments.parsers.habi_parser import HabiParser
from bogota_apartments.parsers.metrocuadrado_parser import MetrocuadradoParser


def get_parser(site_name, logger=None):
    """
    Factory function para obtener el parser apropiado según el sitio web
    
    Args:
        site_name (str): Nombre del sitio web ('metrocuadrado', 'habi')
        logger: Logger opcional
        
    Returns:
        Parser: Instancia del parser apropiado
    """
    parsers = {
        'metrocuadrado': MetrocuadradoParser,
        'habi': HabiParser,
    }
    
    parser_class = parsers.get(site_name.lower())
    if not parser_class:
        raise ValueError(f"No hay parser disponible para: {site_name}")
    
    return parser_class(logger) 