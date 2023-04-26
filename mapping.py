def getCountry():
    list = [['IQ🇮🇶', 'ar-iq']]
    return list


def onType(object_type):
    match object_type:
        case 'movie':
            return '🎬 فيلم'
        case 'show':
            return '📺 عرض'
        case 'tv':
            return '📺 مسلسل'


def onCountry(country):
    list = getCountry()
    for i in list:
        if country == i[1]:
            return i[0]
    return 'لم يتم العثور على'


def onProviders(providers, id):
    for i in providers:
        if id == i['id']:
            return i['clear_name']


def onOfferType(key):
    match key:
        case 'flatrate':
            keytype = 'مشاهدة على الانترنت🖥（مدفوع）'
        case 'free':
            keytype = 'مشاهدة على الانترنت🖥（مجانا）'
        case 'ads':
            keytype = 'مشاهدة على الانترنت🖥（اعلان）'
        case 'buy':
            keytype = 'طريقة الشراء💵（الاستحواذ）'
        case 'rent':
            keytype = 'طريقة الشراء💵（إيجار）'
    return keytype