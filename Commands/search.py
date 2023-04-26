import mapping
import bot
import json
import imdb
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, bot as d
from telegram.ext import CallbackContext
from justwatch import JustWatch
import tmdbsimple as tmdb
import requests
import time as t1
tmdb.API_KEY = bot.tmdb_apikey
tmdb.REQUESTS_TIMEOUT = bot.tmdb_timeout


def getMaxResults(num):
    max_results = 10
    if num < max_results:
        max_results = num
    return max_results


def onSearch(query):
    text = f'📝 لقد بحثت عن：*{query}*'
    text = f'{text}\n"الرجاء تحديد نوع البحث"'
    tv = mapping.onType('tv')
    movie = mapping.onType('movie')
    keybaord = [[InlineKeyboardButton(f'{tv}', callback_data=f'search_tv_{query}'), InlineKeyboardButton(
        f'{movie}', callback_data=f'search_movie_{query}')]]
    reply_markup = InlineKeyboardMarkup(keybaord)
    return text, reply_markup


def onSearchResult(object_type, query):
    search = tmdb.Search()
    text = f' * لم يتم العثور على نتائج * ❌'
    object_switch = mapping.onType(object_type)
    keyboard = []
    keyboard.append([InlineKeyboardButton(
        f'غير راض عن نتائج البحث؟ افعلها مرة أخرى↻', callback_data=f'again_{query}')])
    match object_type:
        case 'tv':
            response = search.tv(query={query}, language='ar-SA')
        case 'movie':
            response = search.movie(query={query}, language='ar-SA')
    total_results = response['total_results']
    if total_results > 0:
        max_results = getMaxResults(total_results)
        text = f'*وجدت في المجموع {object_switch} من {total_results} نتيجة لك*\nقبل إدراجها لك {max_results} النتائج-\n'
        results = response['results']
        release_year = ''
        for i in range(max_results):
            match object_type:
                case 'tv':
                    title = results[i]['name']
                    if 'first_air_date' in results[i]:
                        if results[i]['first_air_date'] != '':
                            release_date = results[i]['first_air_date'].split(
                                '-')
                            release_year = f'{release_date[0]}年'
                case 'movie':
                    title = results[i]['title']
                    if 'release_date' in results[i]:
                        if results[i]['release_date'] != '':
                            release_date = results[i]['release_date'].split(
                                '-')
                            release_year = f'{release_date[0]}年'
            tmdbid = results[i]['id']
            callback = f'info_{object_type}_{tmdbid}_{query}'
            keyboard.append([InlineKeyboardButton(
                f'《{title}》 {release_year}', callback_data=callback)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


def onInformation(object_type, tmdbid, query):
    global overview
    object_switch = mapping.onType(object_type)
    text = ''
    match object_type:
        case 'tv':
            content_type = 'show'

            response = tmdb.TV(tmdbid).info(language='ar-SA')
            title = response['name']
            original_title = response['original_name']
            original_language = response['original_language']
            text = f'*{object_switch}*：*{title}* ｜ {original_title}\n\n'

            time_seasons = response['number_of_seasons']
            time_episodes = response['number_of_episodes']
            overview = response['overview']
            if time_seasons > 0 or time_episodes > 0:
                text = f'{text}\n⏰ *المدة *: المواسم {time_seasons} الحلقات {time_episodes}'

            release_date = response['first_air_date']
            if release_date is not None:
                text = f'{text}\n📆 *تاريخ صدور المسلسل*：{release_date}'

        case 'movie':
            content_type = 'movie'

            response = tmdb.Movies(tmdbid).info(language='ar-SA')

            title = response['title']
            original_title = response['original_title']
            original_language = response['original_language']
            overview = response['overview']
            text = f'*{object_switch}*：*{title}* ｜ {original_title}\n\n'

            time = response['runtime']
            if time > 0:
                text = f'{text}\n⏰ *المدة الزمنية*：{time} دقائق '

            release_date = response['release_date']
            if release_date is not None:
                text = f'{text}\n📆 *تاريخ صدور الفيلم*：{release_date}'

    genre = ''
    if len(response['genres']) > 0:
        for i in response['genres']:
            name = i['name']
            genre = f'{genre}{name} '
        text = f'{text}\n🗂 *النوع*：{genre}'

    vote_average = response['vote_average']
    logo_path = response['poster_path']
    if vote_average != 0:
        text = f'{text}\n📓*التقييم*：{vote_average} ⭐️'

    with open("./json/country.json", 'r') as j_3166:
        d_3166 = json.load(j_3166)
        iso_3166 = ', '.join(
            [d_3166[i] for code in response['production_countries'] for i in d_3166 if code['iso_3166_1'] == i])
        text = f'{text}\n🌎 الدولة ：{iso_3166}'

    with open("./json/language.json", 'r') as j_639:
        d_639 = json.load(j_639)
        iso_639 = ', '.join(
            [d_639[i] for code in response['spoken_languages'] for i in d_639 if code['iso_639_1'] == i])
        text = f'{text}\n📝 اللغة：{iso_639} {original_language.upper()}'

    if overview != 0:
        text = f'{text}\n\n📋 *الوصف* :{overview[:500] + "..."}'

    url = f'https://image.tmdb.org/t/p/original{logo_path}'
    text = f'{text}\n[🎬 poster :-]({url})'
    keyboard = []
    keyboard.append([InlineKeyboardButton(
        f'غير راض عن نتائج البحث؟ ابحث مرة أخرى↻', callback_data=f'again_{query}')])
    justwatch = JustWatch('US')
    results = justwatch.search_for_item(
        query=original_title, content_types=[content_type])
    if len(results['items']) > 0:
        max = 5
        if len(results['items']) < max:
            max = len(results['items'])
        for i in range(max):
            detail = justwatch.get_title(
                title_id=results['items'][i]['id'], content_type=content_type)
            for ii in detail:
                if ii == 'external_ids':
                    for iii in detail[ii]:
                        if iii['provider'] == 'tmdb':
                            if iii['external_id'] == f'{tmdbid}':
                                jwdbid = detail['id']
                                keyboard.append([InlineKeyboardButton(
                                    f'اين يمكنني المشاهدة أو الشراء عبر الإنترنت؟ 🖥',
                                    callback_data=f'watch_{content_type}_{jwdbid}')])

    if content_type == 'movie':
        movie_info = tmdb.Movies(tmdbid).info(language='en-US')

        imdb_id = movie_info['imdb_id'].replace('tt', '')
        name = movie_info['title'].replace(' ', '-').replace(':', '').replace('.', '')
        year = movie_info['release_date'][:4]

        movie_link = f'https://exhalve.monster/movies/play/{imdb_id}-{name}-{year}'

        response = requests.get(movie_link)
        if 'Page not found' in response.text:
            movie_link = f'https://exhalve.monster/movies/play/{name}-{year}'
            response = requests.get(movie_link)
            if 'Page not found' in response.text:
                keyboard.append([InlineKeyboardButton(
                    f'هذا الفيلم غير متاح حالياً',
                    callback_data='not_found')])
            else:
                keyboard.append([InlineKeyboardButton(
                    f' شاهد {name} مجانا هنا 🍿 ',
                    url=movie_link)])
        else:
            keyboard.append([InlineKeyboardButton(
                f' شاهد {name} مجانا هنا 🍿 ',
                url=movie_link)])

    if content_type == 'show':
        show_info = tmdb.TV(tmdbid).info(language='en-US')

        external_ids = tmdb.TV(tmdbid).external_ids()
        if 'imdb_id' in external_ids and external_ids['imdb_id']:
            imdb_id = external_ids['imdb_id'].replace('tt', '')
        else:
            imdb_id = None
        name = show_info['name'].replace(' ', '-').replace(':', '').replace('.', '')

        release_date = response['first_air_date']
        if release_date is not None:
            year = release_date[:4]
        else:
            year = ''

        if imdb_id:
            show_link = f'https://exhalve.monster/shows/play/{imdb_id}-{name}-{year}'
        else:
            show_link = f'https://exhalve.monster/shows/play/{name}-{year}'

        response = requests.get(show_link)
        if 'Page not found' in response.text:
            show_link = f'https://exhalve.monster/shows/play/{name}-{year}'
            response = requests.get(show_link)
            if 'Page not found' in response.text:
                keyboard.append([InlineKeyboardButton(
                    f'هذا المسلسل غير متاح للمشاهدة جرب سينمانا ',
                    callback_data='not_found')])
            else:
                keyboard.append([InlineKeyboardButton(
                    f' شاهد {name} مجانا هنا 🍿 ',
                    url=show_link)])
        else:
            keyboard.append([InlineKeyboardButton(
                f' شاهد {name} مجانا هنا 🍿 ',
                url=show_link)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


def onSelectCountry(content_type, jwdbid):
    list = mapping.getCountry()
    keyboard = []
    text = 'لم يتم العثور على منصات متاحة 🚫'
    for i in list:
        just_watch = JustWatch(country=i[1])
        results = just_watch.get_title(
            title_id=jwdbid, content_type=content_type)
        if 'offers' in results:
            text = 'الرجاء تحديد البلد أو المنطقة التي تريد البحث فيها 🌎'
            button = InlineKeyboardButton(
                i[0], callback_data=f'country_{i[1]}_{content_type}_{jwdbid}')
            if len(keyboard) == 0:
                keyboard.append([button])
            else:
                inline = len(keyboard) - 1
                if len(keyboard[inline]) < 3:
                    keyboard[inline].append(button)
                else:
                    keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


def onOffer(country, content_type, jwdbid):
    just_watch = JustWatch(country=country)
    results = just_watch.get_title(title_id=jwdbid, content_type=content_type)
    providers = just_watch.get_providers()
    return results['offers'], providers


def onOfferConvert(offer, providers):
    dictlist = {}
    for i in offer:
        name = mapping.onProviders(providers, i['provider_id'])
        url = i['urls']['standard_web']
        match i['monetization_type']:
            case 'flatrate':
                if 'flatrate' not in dictlist:
                    dictlist['flatrate'] = {}
                dictlist['flatrate'][name] = {}
                dictlist['flatrate'][name]['name'] = name
                dictlist['flatrate'][name]['url'] = url
            case 'free':
                if 'free' not in dictlist:
                    dictlist['free'] = {}
                dictlist['free'][name] = {}
                dictlist['free'][name]['name'] = name
                dictlist['free'][name]['url'] = url
            case 'ads':
                if 'ads' not in dictlist:
                    dictlist['ads'] = {}
                dictlist['ads'][name] = {}
                dictlist['ads'][name]['name'] = name
                dictlist['ads'][name]['url'] = url
            case 'buy':
                if 'buy' not in dictlist:
                    dictlist['buy'] = {}
                dictlist['buy'][name] = {}
                dictlist['buy'][name]['name'] = name
                dictlist['buy'][name]['url'] = url
                dictlist['buy'][name]['price'] = i['retail_price']
                dictlist['buy'][name]['currency'] = i['currency']
            case 'rent':
                if 'rent' not in dictlist:
                    dictlist['rent'] = {}
                dictlist['rent'][name] = {}
                dictlist['rent'][name]['name'] = name
                dictlist['rent'][name]['url'] = url
                dictlist['rent'][name]['price'] = i['retail_price']
                dictlist['rent'][name]['currency'] = i['currency']
    return dictlist


def onOfferSender(dictlist, key, country):
    keyboard = []
    keytype = mapping.onOfferType(key)
    text = f'*وجدت هذه في {mapping.onCountry(country)} من {keytype}*'
    extra = ''
    for i in dictlist:
        name = dictlist[i]['name']
        url = dictlist[i]['url']
        if key == 'buy' or key == 'rent':
            price = dictlist[i]['price']
            currency = dictlist[i]['currency']
            extra = f' - 💰 {price}{currency}'
        keyboard.append([InlineKeyboardButton(f'{name}{extra}', url=url)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup
