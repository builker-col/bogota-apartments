import numpy as np
import unidecode
import pandas as pd

def normalize_barrio(x):
    NOMBRES_BARRIOS = {
        'CHAPINERO': ['CHAPINER0', "CHA'PINERO", 'CAPINERO', 'CHAPINERRO', 'CAHPINERO', 'CHAPIENERO', 'PARKWAY', 'CHAPONERO', 'PARK WAY'],
        'CEDRITOS': ['CEDITOS', 'CEDRITIOS', 'CREDRITOS', 'CEDRITO', 'CEDRO SALAZAR', 'VILLAS DEL MEDITERRANEO', 'CONJUNTO BOSQUES DE LA CANADA', 'SEPTIMA AVENIDA'],
        'PALERMO': ['PELERMO'],
        'MARLy': ['MARLEY'],
        'SANTA BARBARA': ['SANTA BARABARA', 'SANTA B ARBARA', 'STA BARBARA ORIENTAL', 'STA BARBARA', 'SANRA BARBARA CENTRAL', 'SANTABARBARA', 'BUGANVILLA'],
        'ANTIGUO COUNTRY': ['ANTIGUO CONTRY'],
        'SAN LUIS': ['SANNLUIS'],
        'MONTEARROYO': ['MONTEARROYO NORTE'],
        'MARTIRES': ['LOS MARTIREZ'],
        'ALAMOS': ['ALAMO'],
        'LA PORCIUNCULA': ['PORCINCULA'],
        'BELALCAZAR': ['BELARCAZAR'],
        'CABRERA': ['CABRRERA'],
        'SAN CRISTOBAL NORTE': ['SAN CRISTOBAL NORTE 170 Y ALREDORES'],
        'PUENTE LARGO': ['PUENTELARGO'],
        'QUINTA PAREDES': ['QUINTAPAREDES'],
        'ENTRERIOS': ['ENTRERRIOS'],
        'CASA BLANCA': ['CASABLANCA'],
        'BOSQUE MEDINA': ['BOSQUE DE MEDINA', 'BOSQUE MEDIANA', 'BOSQUES DE MEDINA'],
        'TIBABITA': ['BARRIO TIBABITA', 'TIBATITA'],
        'LAS ACACIAS': ['LAS ACASIAS'],
        'CHICO NORTE': ['CHIC? NORTE'],
        'KENNEDY': ['CIUDAD KENEDY'],
        'CANDELARIA ANTIGUA': ['CANDELARIA LA ANTIGUA'],
        'LA CASTELLANA': ['CASTELLANA'],
        'SANTA BARBARA ALTA': ['SANTA BARBA ALTA'],
        'SAN PATRICIO': ['SAN PATRICO'],
        'EL VERBENAL': ['EL VERVENAL'],
        'SANTA BIBIANA': ['SANTA VIVIAN'],
        'PORTAL DE BRASIL': ['EL PORTAL DEL BRAZIL'],
        'LA FELICIDAD': ['LAFELICIDAD'],
        'SANTA HELENA': ['STA HELENA DE BAVIERA'],
        'MOLINOS NORTE': ['MOLINOS DEL NORTE'],
        'PRADERA NORTE': ['PRADERA DEL NORTE'],
        'SANTA RITA': ['SANTARITA'],
        'METROPOLIS': ['METRA3POLIS', 'JOSE JOAQUIN VARGAS', 'J VARGAS'],
        'SAUZALITO': ['SAUSALITO'],
        'RECODO DEL COUNTRY': ['RECODO DEL COUNTTRY', 'RECODO DEL CONTRY'],
        'CERROS DE SOTILEZA': ['CERROS DE SOLTILEZA'],
        'BATAN': ['BATAM'],
        'LINDARAJA': ['LINDAJARA', 'LINDARAJJA'],
        'VILLAS DE GRANADA': ['VILLAS DE GRANANA'],
        'LA CALLEJA': ['LA CALLELJA'],
        'ORQUIDEAS': ['ARCADIA', 'EDIFICIO CIENTO 63'],
        'COUNTRY': ['BOSQUE DE LA RESERVA']
    }

    try:
        x = unidecode.unidecode(x).upper()
        for key, value in NOMBRES_BARRIOS.items():
            for v in value:
                if v in x:
                    return key
        return x
    except:
        return np.nan
    
def change_barrio(df: pd.DataFrame):
    df.barrio[df.barrio == 'SIN DEFINIR'] = np.nan
    df.barrio[df.barrio == 'BOGOTA D C'] = np.nan
    df.barrio[df.barrio == 'BOGOTA'] = np.nan
    df.barrio[df.barrio == 'KAHLO 51'] = 'CHAPINERO'
    df.barrio[df.barrio == 'CR 4 69 32'] = 'CHAPINERO'
    df.barrio[df.barrio == 'ALIANZA 60'] = 'CHAPINERO'
    df.barrio[df.barrio == 'MUSEO NACIONAL'] = 'SANTA FE'
    df.barrio[df.barrio == 'CERROS ORIENTALES'] = 'CHAPINERO'
    df.barrio[df.barrio == 'MONTERESERVA'] = 'NIZA'
    df.barrio[df.barrio == 'BOSQUE VERDE'] = 'NIZA'
    df.barrio[df.barrio == 'SIERRAS DEL ESTE'] = 'CHAPINERO'
    df.barrio[df.codigo == '5175-3617'] = 'CHAPINERO'
    df.barrio[df.codigo == '34-M4009003'] = 'ENGATIVA'
    df.barrio[df.barrio == 'KANDINSKY'] = 'CHAPINERO'
    df.barrio[df.barrio == 'EDIFICIO SAINT PAUL'] = 'CHAPINERO'
    df.barrio[df.barrio == 'EL ROSAL'] = 'CHAPINERO'
    df.barrio[df.codigo == '450-M2536448'] = 'CHICO NORTE'
    df.barrio[df.barrio == 'CALLE 170 PRICEMART'] = 'USAQUEN'
    df.barrio[df.barrio == 'AUTOPISTA NORTE CALLE 170'] = 'USAQUEN'
    df.barrio[df.barrio == 'EDIFICIO LAYA 119 P H'] = 'USAQUEN'
    df.barrio[df.barrio == 'EDIFICIO MORAL VI P H'] = 'CEDRITOS'
    df.barrio[df.barrio == 'RECREO FE LOS FRAILES (ANTES B'] = 'SUBA'
    df.barrio[df.barrio == 'NELEKONAR 2'] = 'USAQUEN'
    df.barrio[df.barrio == 'CONJUNTO CALATAYUD'] = 'SUBA'
    df.barrio[df.barrio == 'ZONA 5'] = 'FONTIBON'
    df.barrio[df.barrio == 'LAS MERCEDARIAS'] = 'SANTA FE'
    df.barrio[df.barrio == 'VALLADOLID'] = 'KENNEDY'
    df.barrio[df.barrio == 'VILLA VERONCA ETAPA 1'] = 'KENNEDY'
    df.barrio[df.barrio == 'BOHIOS'] = 'FONTIBON'
    df.barrio[df.barrio == 'CALATAYUD'] = 'SUBA'
    df.barrio[df.barrio == 'CERROS OCCIDENTALES'] = 'SUBA'
    df.barrio[df.barrio == 'ESCUELA DE CARABINEROS'] = 'SUBA'
    df.barrio[df.barrio == 'QUMRAN'] = 'SUBA'
    df.barrio[df.barrio == 'VALLE DEL REFOUS'] = 'SUBA'
    df.barrio[df.barrio == 'EDIFICIO DAVIS'] = 'CHAPINERO'
    df.barrio[df.barrio == 'SABANA DE TIERRA'] = 'KENNEDY'
    df.barrio[df.barrio == 'BOSQUES DE LA CANADA'] = 'USAQUEN'
    df.barrio[df.barrio == 'TORRE LADERA'] = 'SUBA'
    df.barrio[df.barrio == 'BOSQUES DEL MARQUES'] = 'USAQUEN'
    df.barrio[df.barrio == 'FOLEDO'] = 'USAQUEN'
    df.barrio[df.barrio == 'MONTE RESERVA'] = 'SUBA'
    df.barrio[df.barrio == 'PLENITUD'] = 'USAQUEN'
    df.barrio[df.barrio == 'TORRES DE PALO ALTO'] = 'SUBA'
    df.barrio[df.barrio == 'LAS DOS AVENIDAS I ETAPA'] = 'KENNEDY'
    df.barrio[df.barrio == 'BRASIL II SEGUNDA ETAPA'] = 'KENNEDY'

def assing_localidad(barrio):
    usaquen = ['SANTA BARBARA', 'CEDRITOS', 'USAQUEN', 'RINCON DEL PUENTE',
               'VERBENAL', 'LA URIBE', 'SAN CRISTOBAL NORTE',
               'TOBERIN', 'COUNTRY CLUB', 'SANTA ANA', 'VILLAS DE ANDALUCIA',
               'SAN ANTONIO NORTE', 'ACACIAS', 'ENTREMONTES', 'SANTA COLOMA',
               'CEDRO BOLIVAR', 'CEDITROS', 'CEDROS', 'SERRAMONTE',
               'BELMIRA', 'SAN ANTONIO', 'CEDRO GOLF', 'LA CAROLINA',
               'SANTA TERESA', 'BARRANCAS', 'CAMPO ALEGRE', 'BELLA SUIZA',
               'SAN PATRICIO', 'MULTICENTRO', 'CALLEJA', 'BOSQUE MEDINA',
               'BOSQUE DE PINOS', 'SANTA BIBIANA', 'SANTA PAULA', 'IRAKA',
               'EL CONTADOR', 'SIERRAS DEL MORAL', 'EL REDIL', 'ICATA',
               'DARDANELO', 'NAVARRA', 'MARANTA', 'LA LIBERIA', 'GINEBRA',
               'CONTADOR', 'MONTEARROYO', 'EL PEDREGAL', 'CEDRO NARVAEZ',
               'LIJACA', 'TIBABITA', 'ALTA BLANCA', 'EL VERBENAL', 'CODITO',
               'MOLINOS NORTE', 'HORIZONTE NORTE', 'SIERRA DEL MORAL',
               'PRADERA NORTE', 'RESERVA DE LA SIERRA', 'PARQUES DE LORENA',
               'SAN PARTICIO', 'ORQUIDEAS', 'CAOBOS SALAZAR', 'VILLA DEL MEDITERRANEO',
               'BOSQUE DE LA CANADA', 'BARRACAS', 'CEDRO NORTE', 'RINCON DEL CEDRO',
               'MONTELOMA', 'HORIZONTES NORTE', 'NUEVA AUTOPISTA', 'LA CALLEJA',]

    chapinero = ['CHAPINERO', 'ROSALES', 'EMAUS', 'CHICO', 'EL LAGO',
                 'NOGAL', 'REFUGIO', 'BELLAVISTA', 'ZONA G', 'LA ESPERANZA',
                 'LA SALLE', 'MARLY', 'BOSQUE CALDERON', 'JAVERIANA',
                 'PORCIUNCULA', 'PARDO RUBIO', 'SUCRE', 'PARDU', 'NUEVA GRANADA',
                 'QUINTA CAMACHO', 'CATALUNA', 'CABRERA', 'MARIA CRISTINA',
                 'ROBLES', 'ALTOS DEL CASTILLO', 'INGEMAR', 'ALTOS DEL BOSQUE',
                 'VIRREY', 'EL RETIRO', 'ANTIGUO COUNTRY', 'COUNTRY', 'RETIRO',
                 'EL CASTILLO', 'ROSAL RESERVADO', 'GRANADA', 'MARIA CRISTIANA',
                 'LAGO GAITAN', 'LOS CERROS', 'NORTE', 'CASTILLO', 'ESPARTILLAL']

    santa_fe = ['PARQUE CENTRAL BAVARIA', 'SAN DIEGO', 'CENTRO INTERNACIONAL',
                'SAN MARTIN', 'SAMPER', 'BOSQUE IZQUIERDO', 'LAS AGUAS',
                'LA MACARENA', 'PERSEVERANCIA', 'ALAMEDA', 'LA INDEPENDENCIA',
                'VERACRUZ', 'LAS NIEVES', 'SANTA INES', 'EL DORADO',
                'SAGRADO CORAZON', 'LOURDES', 'SANTA FE', 'CENTRO']

    san_cristobal = ['SAN CRISTOBAL', 'RAMAJAL', '20 DE JULIO', 'LAS BRISAS',
                     'VALPARAISO', 'BOSQUE LA RESERVA', 'BELLO HORIZONTE',
                     'CALVO SUR', 'CORDOBA', 'LOS ALPES', 'CAPELLANIA',
                     'QUINTA RAMOS', 'SANTA RITA', 'LA MARIA', 'LONDRES',
                     'CORINTO', 'VILLA JAVIER']

    usme = ['USME', 'ALEJANDRIA', 'EL PORVENIR', 'PORVENIR', 'EL BOSQUE']

    tunjuelito = ['TUNJUELITO', 'NUEVO MUZU', 'CIUDAD TUNAL', 'EL CARMEN',
                  'BRAVO PAEZ', 'TUNAL', 'SAN CARLOS']

    bosa = ['BOSA', 'EL PORVENIR III', 'DANUBIO', 'SAN BERNARDINO', 'EL CORZO',
            'PORTAL DE BRASIL', 'GUALOCHE', 'PABLO VI', 'VILLA DEL RIO',
            'NUEVO RECREO', 'VILLAS DEL PROGRESO']

    kennedy = ['KENNEDY', 'CASTILLA', 'TINTALA', 'CALANDAIMA', 'TINTAL',
               'TUNDAMA', 'MARSELLA', 'SANTA PAZ', 'LA IGUALDAD', 'LOS PANTANOS',
               'PIO', 'OSORIO', 'MILENTA II', 'GALAN', 'VILLA ALSACIA',
               'EL PORTAL DE PATIO BONITO', 'SAN ANDRES', 'ALSACIA', 'ALOHA',
               'CONDADO', 'BOSCONIA', 'ANDALUCIA', 'TIMIZA', 'TECHO', 'FAVIDI',
               'PATIO BONITO', 'PLAZA DE LA AMERICAS', 'CARIMAGUA', 'MANDALAY',
               'VILLA CLAUDIA', 'CLASS', 'TIERRA BUENA', 'VILLA ADRIANA',
               'IPANEMA', 'BOITA', 'SANTA CATALINA', 'ROMA', 'CIUDAD DON BOSCO']

    fontibon = ['FONTIBON', 'MODELIA', 'ZONA FRANCA', 'EL VERGEL', 'VILLEMAR',
                'LA FELICIDAD', 'EL RECODO', 'CHANCO', 'SAN PABLO JERICO',
                'HAYUELOS', 'EL TINTAL', 'SAUZALITO', 'VILLA ANDREA', 'EL RUBI',
                'ATAHUALPA', 'COFRADIA', 'MONTECARLO', 'PUEBLO NUEVO', 'BOSTON',
                'PUENTE GRANDE']

    engativa = ['ENGATIVA', 'GRAN GRANADA', 'LA GRANJA', 'LA ESPANOLA', 'NORMANDIA',
                'LAS FERIAS', 'PARIS', 'BOSQUE POPULAR', 'CEREZOS', 'ALAMOS',
                'ESTRADA', 'LOS ANGELES', 'LOS LAURELES', 'FLORENCIA', 'BOCHICA',
                'EL CORTIJO', 'BOYACA', 'EL LAUREL', 'SANTA ROSA', 'CORTIJO',
                'CIUDADELA COLSUBSIDIO', 'SAN IGNACIO', 'EL LUJAN', 'LA RIVIERA',
                'MINUTO DE DIOS', 'VILLA LUZ', 'LOS MONJES', 'SANTA HELENITA',
                'BACHUE', 'VILLA TERESITA', 'GARCES NAVAS', 'EL GACO', 'TORRE CAMPO',
                'FLORIDA BLANCA', 'VILLAS DE GRANADA']

    suba = ['SUBA', 'GRANADA NORTE', 'PASADENA', 'PONTEVEDRA', 'COLINA CAMPESTRE',
            'TUNA BAJA', 'BATAN', 'PUENTE LARGO', 'MORATO', 'GRATAMIRA', 'MAZUREN',
            'LINDARAJA', 'GILMAR', 'ALHAMBRA', 'TUNA ALTA', 'ATABANZA', 'MONACO',
            'NIZA', 'MANUELITA', 'SOTILEZA', 'CALATRAVA', 'COLINA', 'LAGARTOS',
            'IBERIA', 'CANTALEJO', 'VICTORIA NORTE', 'SANTA HELENA', 'BRITALIA',
            'LAS ORQUIDEAS', 'TIBABUYES', 'LISBOA', 'BOSQUES DE SAN JORGE', 'MIRANDELA',
            'POTOSI', 'JULIO FLORES', 'LAS VILLAS', 'EL PLAN', 'EL PINO', 'CASA BLANCA',
            'PRADO VERANIEGO', 'PRADO PINZON', 'NUEVA ZELANDIA', 'VILLA DEL PRADO',
            'LAS FLORES', 'LOMBARDIA', 'BILBAO', 'GUAYMARAL', 'SANTA MARGARITA',
            'CAMPANELLA', 'LOS NARANJOS', 'TIERRA LINDA', 'SAN NICOLAS', 'ARRAYANES',
            'CARMEL CLUB', 'LA FLORESTA', 'LAS TERRAZAS', 'EL PINAR', 'NUEVO CORINTO',
            'CERROS DE SAN JORGE', 'MALIBU', 'PRADO', 'PROVENZA', 'VILLA ELISA',
            'LOS ELISEOS', 'AURES', 'DEL MONTE', 'ILARCO', 'ALAMBRA', 'SAN CIPRIANO',
            'BOSQUES DE ALAVA', 'PORTALES DEL NORTE', 'CANTAGALLO', 'CERROS DE SOTILEZA',
            'LA FRANCIA', 'TORRELADERA', 'PINAR', 'RECREO DE LOS FRAILES', 'ALTOS DE BACATA']

    teusaquillo = ['TEUSAQUILLO', 'GALERIAS', 'SAN LUIS', 'ARMENIA',
                   'LA SOLEDAD', 'ARMENIA', 'LA MAGDALENA', 'PALERMO',
                   'BANCO CENTRAL', 'CAMPIN', 'BELALCAZAR', 'SOLEDAD',
                   'QUINTA PAREDES', 'ESTRELLA', 'SANTA TERESITA', 'FEDERMAN',
                   'SALITRE', 'DIVINO SALVADOR', 'ALFONSO LOPEZ', 'QUESADA',
                   'LAS AMERICAS', 'RAFAEL NUNEZ', 'EL RECUERDO', 'PAULO VI',
                   'GRAN AMERICA', 'LA ESMERALDA', 'CARLOS LLERAS', 'QUIRINAL']

    puente_aranda = ['PUENTE ARANDA', 'VILLA INES', 'TIBANA', 'LA ASUNCION',
                     'ALCALA', 'ALQUERIO', 'COLON', 'SAN GABRIEL', 'LA PRADERA',
                     'PRIMAVERA', 'SAN EUSEBIO']

    rafael_uribe = ['RAFAEL URIBE URIBE', 'SOCIEGO', 'INGLES', 'MARRUECOS',
                    'CENTENARIO ', 'SAN JOSE', 'RAFAEL URIBE NORTE', 'MURILLO TORO',
                    'LA RESURRECCION', 'CENTENARIO', 'MARCO FIDEL SUAREZ', 'MOLINOS',
                    'RAFAEL URIBE']

    ciudad_bolivar = ['CIUDAD BOLIVAR', 'CHICALA', 'RAFAEL ESCAMILLA', 'GALICIA',
                      'MADELENA', 'ATLANTA', 'LA MILAGROSA', 'CANDELARIA LA NUEVA',
                      'PERDOMO', 'EL ENSUENO', 'LA ESTANCIA', 'CALABRIA', 'SAN JOAQUIN',
                      'SOTAVENTO', 'COMPARTIR', 'SAN RAFAEL']

    barrios_unidos = ['BARRIOS UNIDOS', '7 DE AGOSTO', 'SIETE DE AGOSTO', 'BENJAMIN HERRERA',
                      'ALCAZARES', 'MUEQUETA', 'BAQUERO', 'QUINTA MUTIS', 'SAN MIGUEL',
                      'EL POLO', 'LOS ANDES', 'JORGE ELIECER GAITAN', 'LA PAZ', 'POLO CLUB',
                      'PATRIA', 'SAN FELIPE', 'ENTRERIOS', 'SIMON BOLIVAR', 'SAN FERNANDO',
                      'LA CASTELLANA', 'ANDES', 'METROPOLIS', 'CONCEPCION NORTE']

    martirez = ['MARTIRES', 'VERAGUAS', 'PALOQUEMAO', 'VERGEL', 'SANTA ISABEL', 'RICAURTE', 
                'LA FAVORITA', 'EL LISTON']

    la_candelaria = ['LA CATEDRAL', 'LA CONCORDIA', 'SAN BERNANDINO', 'CANDELARIA CENTRO HISTORICO',
                     'CANDELARIA ANTIGUA', 'LA CANDELARIA', 'CANDELARIA']

    antonio_nariño = ['FRAGUITA', 'SANTANDER SUR', 'RESTREPO', 'CIUDAD BERNA', 'ANTONIO NARINO',
                      'FRAGUA', 'CIUDAD JARDIN']

    try:
        barrio = unidecode.unidecode(barrio).upper()

        for i in chapinero:
            if i in barrio:
                return 'CHAPINERO'

        for i in usaquen:
            if i in barrio:
                return 'USAQUEN'

        for i in santa_fe:
            if i in barrio:
                return 'SANTA FE'

        for i in san_cristobal:
            if i in barrio:
                return 'SAN CRISTOBAL'

        for i in usme:
            if i in barrio:
                return 'USME'

        for i in tunjuelito:
            if i in barrio:
                return 'TUNJUELITO'

        for i in bosa:
            if i in barrio:
                return 'BOSA'

        for i in kennedy:
            if i in barrio:
                return 'KENNEDY'

        for i in fontibon:
            if i in barrio:
                return 'FONTIBON'

        for i in engativa:
            if i in barrio:
                return 'ENGATIVA'

        for i in suba:
            if i in barrio:
                return 'SUBA'

        for i in teusaquillo:
            if i in barrio:
                return 'TEUSAQUILLO'

        for i in puente_aranda:
            if i in barrio:
                return 'PUENTE ARANDA'

        for i in rafael_uribe:
            if i in barrio:
                return 'RAFAEL URIBE URIBE'

        for i in ciudad_bolivar:
            if i in barrio:
                return 'CIUDAD BOLIVAR'

        for i in barrios_unidos:
            if i in barrio:
                return 'BARRIOS UNIDOS'

        for i in martirez:
            if i in barrio:
                return 'MARTIRES'
            
        for i in la_candelaria:
            if i in barrio:
                return 'LA CANDELARIA'
            
        for i in antonio_nariño:
            if i in barrio:
                return 'ANTONIO NARIÑO'

        else:
            return 'OTRO'
    except:
        return np.nan
