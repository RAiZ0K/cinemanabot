import logging
from turtle import update
import requests
from uuid import uuid4
import urllib.parse

from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, \
    InputTextMessageContent, ChatAction, Bot, ChatPermissions
import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters, \
    commandhandler, InlineQueryHandler

import Commands.search as SearchCommand
import Commands.top as TodayCommand

bot_token = '5477126979:AAECFLQZdqOMrzxBi3Yyi7j0QJxMlYy_nUc'

tmdb_apikey = 'de9bdc9d2a6bebf77410b5fc0c7adb64'
tmdb_timeout = 5

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, filename='recording.log',
    filemode='a'
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    chat_member = context.bot.get_chat_member(chat_id='@boboimylife', user_id=user_id)

    if chat_member.status == 'left':
        context.bot.send_message(chat_id=chat_id, text="من فضلك اشترك بالقناة لاستخدام البوت.\n\n\n @boboimylife")
    elif update.effective_chat.type == 'private':
        text = "مرحبا!\nمن خلال هذا البوت سوف تستطيع معرفة جميع تفاصيل الفيلم الذي تريد.\n فقط أرسل الاسم وسيظهر لك.\n الأوامر:\n/today  لعرض قائمة الترند من الأفلام والمسلسلات\n/acts  لعرض الأعمال الخاصة بالممثل - اسم الممثل\n/actor  لعرض السيرة الذاتية الخاصة بالممثل - اسم الممثل\n/acts_ar  لعرض الأعمال الخاصة بالممثل بالعربي - اسم الممثل\n\n`@mlvlbot jason statham`  ضع يوزر البوت وبعدها اسم أي ممثل للبحث عنه."
        context.bot.send_photo(chat_id=update.effective_message.chat_id,
                               photo='https://deadline.com/wp-content/uploads/2021/05/House-Of-Dragons-HBO.jpg',
                               caption=text)
    else:
        try:
            text = "مرحبا بكم! للاستفادة من خدمات البوت يرجى إضافة '!' قبل اسم الفيلم او المسلسل المطلوب البحث عنه. مثل `the godfather !` \n\n /today   لعرض قائمة الترند من الأفلام والمسلسلات\n /acts  لعرض الأعمال الخاصة بالممثل - اسم الممثل\n /actor  لعرض السيرة الذاتية الخاصة بالممثل - اسم الممثل\n /acts_ar  لعرض الأعمال الخاصة بالممثل بالعربي - اسم الممثل\n\nللبحث عن ممثل معين، ارسل `@mlvlbot اسم الممثل`"
            context.bot.send_photo(chat_id=update.effective_message.chat_id,
                                   photo='https://deadline.com/wp-content/uploads/2021/05/House-Of-Dragons-HBO.jpg',
                                   caption=text)
        except Exception as error:
            logging.error(error)


def today(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    chat_member = context.bot.get_chat_member(chat_id='@boboimylife', user_id=user_id)

    if chat_member.status == 'left':
        context.bot.send_message(chat_id=chat_id, text="من فضلك اشترك بالقناة لاستخدام البوت.\n\n\n @boboimylife")
    else:
        try:
            text, reply_markup = TodayCommand.onTrending('today')
            update.message.reply_markdown(
                text, reply_markup=reply_markup)
            context.bot.send_sticker(chat_id=update.effective_message.chat_id,
                                     sticker='CAACAgIAAxkBAAICZGMF58-VQjKB485Yzf58hpuhYH1LAAKFHAACkjIoSGcF0fYzjwa5KQQ')
        except Exception as error:
            logging.error(error)


def search(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    chat_member = context.bot.get_chat_member(chat_id='@boboimylife', user_id=user_id)

    if chat_member.status == 'left':
        context.bot.send_message(chat_id=chat_id,
                                 text="Please subscribe to the channel to use the bot.\n\n\n @boboimylife")
        return

    if update.effective_chat.type == 'private':
        try:
            context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

            text, reply_markup = SearchCommand.onSearch(update.message.text)
            update.message.reply_markdown(text, reply_markup=reply_markup)

            context.bot.send_sticker(chat_id=chat_id,
                                     sticker='CAACAgIAAxkBAAICe2MF6U5MYQOabNvvUcJc0g75FNxBAALdGgACIUAxSDUCE4lXrno6KQQ')
            logging.info(f'{update.message.chat.id}@{update.message.chat.username} - {update.message.text}')
        except Exception as error:
            logging.error(error)
    else:
        if update.message.text.startswith('!'):
            try:
                context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

                message = update.message.text[1:]

                text, reply_markup = SearchCommand.onSearch(message)
                update.message.reply_markdown(text, reply_markup=reply_markup)

                context.bot.send_sticker(chat_id=chat_id,
                                         sticker='CAACAgIAAxkBAAICe2MF6U5MYQOabNvvUcJc0g75FNxBAALdGgACIUAxSDUCE4lXrno6KQQ')
                logging.info(f'{update.message.chat.id}@{update.message.chat.username} - {update.message.text}')
            except Exception as error:
                logging.error(error)


allowed_chat_ids = set()


def message_handler(update, context):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    # Check if the user who added the bot to the group is the bot owner
    if user_id == 1278252233:
        context.bot.send_message(chat_id=chat_id)
    else:
        # If the user who added the bot is not the bot owner, remove the bot from the group
        context.bot.leave_chat(chat_id)
        return

    # Respond to message only if the bot was added by the owner
    context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id)


def actor(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    actor_search_str = ' '.join(context.args)
    encoded_search_str = urllib.parse.quote(actor_search_str)

    # Replace <your_channel_username> with your channel's username or ID
    chat_member = context.bot.get_chat_member(chat_id='@boboimylife', user_id=user_id)

    if chat_member.status == 'left':
        context.bot.send_message(chat_id=chat_id, text="من فضلك اشترك بالقناة لاستخدام البوت.\n\n\n @boboimylife")
    else:
        response = requests.get(
            f'https://api.themoviedb.org/3/search/person?api_key=de9bdc9d2a6bebf77410b5fc0c7adb64&query={encoded_search_str}&page=1&include_adult=false')
        actor_result_dict = response.json()

        if (actor_result_dict.get('total_results')) == 0 or ((actor_result_dict.get('results')[0])[
            'known_for_department']) != 'Acting':
            context.bot.send_message(chat_id=chat_id,
                                     text="لم يتم العثور على نتائج جرب كتابه اسم الممثل بالشكل الصحيح\n\n\n /actor jason statham")

        else:
            actor_id = ((actor_result_dict.get('results')[0])['id'])
            id_query_response = requests.get(
                f'https://api.themoviedb.org/3/person/{actor_id}?api_key=de9bdc9d2a6bebf77410b5fc0c7adb64&language=ar-SA')
            actor_info_dict = id_query_response.json()

            actor_name = ((actor_result_dict.get('results')[0])['name'])
            bio = (actor_info_dict.get('biography'))

            if (
                    len(bio)) > 2048:
                actor_bio = (bio[0:2030] + '.....')
            else:
                actor_bio = bio

            actor_img = ((actor_result_dict.get('results')[0])['profile_path'])

            message = f'<b>Search results for:</b> <i>{actor_search_str}</i>\n\n'
            message += f'<b>{actor_name}</b>\n\n\n\n{actor_bio}\n\n\n\n\n'
            message += f'<a href="https://image.tmdb.org/t/p/original{actor_img}">&#8203;</a>'
            message += '**قائمة الممثلين لا تزال في مرحلة البيتا لن تضهر لك السيرة الخاصة بجميع الممثلين لذلك إن لم تضهر لك السيرة أرسل اسم الممثل إلى هنا RAiZOK#9193 ساعدنا في توسيع قاعدة البيانات**'

            context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)


def acts(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    actor_search_str = ' '.join(context.args)
    encoded_search_str = urllib.parse.quote(actor_search_str)
    chat_member = context.bot.get_chat_member(chat_id='@boboimylife', user_id=user_id)

    if chat_member.status == 'left':
        context.bot.send_message(chat_id=chat_id, text="من فضلك اشترك بالقناة لاستخدام البوت.\n\n\n @boboimylife")

    else:
        response = requests.get(
            f'https://api.themoviedb.org/3/search/person?api_key=de9bdc9d2a6bebf77410b5fc0c7adb64&query={encoded_search_str}&page=1&include_adult=false')
        actor_result_dict = response.json()
        if (actor_result_dict.get('total_results')) == 0 or ((actor_result_dict.get('results')[0])[
            'known_for_department']) != 'Acting':
            update.message.reply_text(
                'لم يتم العثور على نتائج جرب كتابه اسم الممثل بالشكل الصحيح\n\n\n /acts jason statham')
        else:
            actor_id = ((actor_result_dict.get('results')[0])['id'])
            id_query_response = requests.get(
                f'https://api.themoviedb.org/3/person/{actor_id}?api_key=de9bdc9d2a6bebf77410b5fc0c7adb64&language=en-US')
            actor_info_dict = id_query_response.json()

            actor_name = ((actor_result_dict.get('results')[0])['name'])
            actor_img = ((actor_result_dict.get('results')[0])['profile_path'])

            series_response = requests.get(
                f'https://api.themoviedb.org/3/person/{actor_id}/tv_credits?api_key=de9bdc9d2a6bebf77410b5fc0c7adb64&language=en-US')
            series_result_dict = series_response.json()

            series_list = ''
            for series in series_result_dict['cast']:
                series_title = series['name']
                series_list += f'- {series_title}\n'

            n_series = len(series_result_dict['cast'])

            movies_response = requests.get(
                f'https://api.themoviedb.org/3/person/{actor_id}/movie_credits?api_key=de9bdc9d2a6bebf77410b5fc0c7adb64&language=en-US')
            movies_result_dict = movies_response.json()

            movie_list = ''
            for movie in movies_result_dict['cast']:
                movie_title = movie['title']
                movie_list += f'- {movie_title}\n'

            num_movies = len(movies_result_dict['cast'])

        message = f'<b>نتائج البحث عن:</b> <i>{actor_search_str}</i>\n\n'
        message += f'<b>{actor_name}</b>\n\n'
        message += f'<b>المسلسلات الخاصة بالممثل📽 - عددها {n_series} ⥙ </b>\n{series_list}\n\n'
        message += f'<b>الأفلام الخاصة بالممثل📽 - عددها {num_movies} ⥙ </b>\n{movie_list}\n\n'
        message += f'<a href="https://image.tmdb.org/t/p/original{actor_img}">&#8203;</a>'

        message_part1 = message[:2000]
        message_part2 = message[2000:]

        context.bot.send_message(chat_id=update.effective_chat.id, text=message_part1, parse_mode=ParseMode.HTML)
        context.bot.send_message(chat_id=update.effective_chat.id, text=message_part2, parse_mode=ParseMode.HTML)


def acts_ar(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    actor_search_str = ' '.join(context.args)
    encoded_search_str = urllib.parse.quote(actor_search_str)

    chat_member = context.bot.get_chat_member(chat_id='@boboimylife', user_id=user_id)

    if chat_member.status == 'left':
        context.bot.send_message(chat_id=chat_id, text="من فضلك اشترك بالقناة لاستخدام البوت.\n\n\n @boboimylife")
    else:
        response = requests.get(
            f'https://api.themoviedb.org/3/search/person?api_key=de9bdc9d2a6bebf77410b5fc0c7adb64&query={encoded_search_str}&page=1&include_adult=false')
        actor_result_dict = response.json()

        if (actor_result_dict.get('total_results')) == 0 or ((actor_result_dict.get('results')[0])[
            'known_for_department']) != 'Acting':
            update.message.reply_text(
                'لم يتم العثور على نتائج جرب كتابه اسم الممثل بالشكل الصحيح\n\n\n /acts_ar jason statham')

        else:
            actor_id = ((actor_result_dict.get('results')[0])['id'])
            id_query_response = requests.get(
                f'https://api.themoviedb.org/3/person/{actor_id}?api_key=de9bdc9d2a6bebf77410b5fc0c7adb64&language=ar-SA')
            actor_info_dict = id_query_response.json()

            actor_name = ((actor_result_dict.get('results')[0])['name'])
            actor_img = ((actor_result_dict.get('results')[0])['profile_path'])

            series_response = requests.get(
                f'https://api.themoviedb.org/3/person/{actor_id}/tv_credits?api_key=de9bdc9d2a6bebf77410b5fc0c7adb64&language=ar-SA')
            series_result_dict = series_response.json()

            series_list = ''
            for series in series_result_dict['cast']:
                series_title = series['name']
                series_list += f'- {series_title}\n'

            n_series = len(series_result_dict['cast'])

            movies_response = requests.get(
                f'https://api.themoviedb.org/3/person/{actor_id}/movie_credits?api_key=de9bdc9d2a6bebf77410b5fc0c7adb64&language=ar-SA')
            movies_result_dict = movies_response.json()

            movie_list = ''
            for movie in movies_result_dict['cast']:
                movie_title = movie['title']
                movie_list += f'- {movie_title}\n'

            num_movies = len(movies_result_dict['cast'])

            message = f'<b>نتائج البحث عن:</b> <i>{actor_search_str}</i>\n\n'
            message += f'<b>{actor_name}</b>\n\n'
            message += f'<b>المسلسلات الخاصة بالممثل📽 - عددها {n_series} ⥙ </b>\n{series_list}\n\n'
            message += f'<b>الأفلام الخاصة بالممثل📽 - عددها {num_movies} ⥙ </b>\n{movie_list}\n\n'
            message += f'<a href="https://image.tmdb.org/t/p/original{actor_img}">&#8203;</a>'

            message_part1 = message[:2000]
            message_part2 = message[2000:]

            context.bot.send_message(chat_id=update.effective_chat.id, text=message_part1, parse_mode=ParseMode.HTML)
            context.bot.send_message(chat_id=update.effective_chat.id, text=message_part2, parse_mode=ParseMode.HTML)


def inline_search(update: Update, context: CallbackContext):
    query = update.inline_query.query.strip()
    if not query:
        return

    encoded_query_str = urllib.parse.quote(query)
    response = requests.get(
        f'https://api.themoviedb.org/3/search/person?api_key={tmdb_apikey}&query={encoded_query_str}&page=1&include_adult=false')
    actor_result_dict = response.json()

    if actor_result_dict.get('total_results') == 0:
        return

    results = []
    for actor in actor_result_dict.get('results')[:5]:
        actor_id = actor.get('id')
        actor_name = actor.get('name')
        result = InlineQueryResultArticle(
            id=str(actor_id),
            title=actor_name,
            input_message_content=InputTextMessageContent(
                f'/acts {actor_name}',
                parse_mode=ParseMode.HTML
            ),
            thumb_url=f'https://image.tmdb.org/t/p/w185/{actor.get("profile_path")}' if actor.get(
                'profile_path') else None
        )
        results.append(result)

    update.inline_query.answer(results, cache_time=1)


def onCallbackQuery(update, context):
    query = update.callback_query
    calldata = query.data.split("_")
    if calldata[0] == 'poster':
        response = requests.get(f"https://www.themoviedb.org/t/p/original{calldata[1]}")
        context.bot.send_photo(chat_id=query.message.chat_id, photo=response.content)
    elif calldata[0] == 'info':
        text, reply_markup = SearchCommand.onInformation(calldata[1], calldata[2], calldata[3])
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')

        # Add button data for "صور الأبطال" button
    elif calldata[0] == 'characters':
        cast = SearchCommand.getCast(calldata[1], calldata[2])
        keyboard = [
            [InlineKeyboardButton("صور الأبطال", callback_data=f'cast_{calldata[1]}_{calldata[2]}_{calldata[3]}')]]
        if len(cast) > 0:
            for i in range(0, len(cast), 2):
                if i + 1 == len(cast):
                    keyboard.append([InlineKeyboardButton(cast[i], callback_data='null'),
                                     InlineKeyboardButton("❌", callback_data='null')])
                else:
                    keyboard.append([InlineKeyboardButton(cast[i], callback_data='null'),
                                     InlineKeyboardButton(cast[i + 1], callback_data='null')])
        keyboard.append([InlineKeyboardButton(f"⬅️", callback_data=f'back_{calldata[1]}_{calldata[2]}_{calldata[3]}'),
                         InlineKeyboardButton(f"➡️", callback_data=f'next_{calldata[1]}_{calldata[2]}_{calldata[3]}')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text=f"قائمة أبطال {calldata[3]}",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )


def button(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    chat_member = context.bot.get_chat_member(chat_id='@boboimylife', user_id=user_id)

    if chat_member.status == 'left':
        context.bot.send_message(chat_id=chat_id, text="من فضلك اشترك بالقناة لاستخدام البوت.\n\n\n @boboimylife")
    else:
        query = update.callback_query
        query.answer()
        bot = query.bot
        calldata = query.data.split('_')
        calltype = calldata[0]
        match calltype:
            case 'again':
                text, reply_markup = SearchCommand.onSearch(
                    calldata[1])
                query.edit_message_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            case 'search':
                text, reply_markup = SearchCommand.onSearchResult(
                    calldata[1], calldata[2])
                query.edit_message_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            case 'info':
                text, reply_markup = SearchCommand.onInformation(
                    calldata[1], calldata[2], calldata[3])
                query.edit_message_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            case 'watch':
                message = bot.send_message(
                    chat_id=update.effective_message.chat_id,
                    text='البحث عن البلدان المتاحة ...',
                    parse_mode=ParseMode.MARKDOWN
                )
                text, reply_markup = SearchCommand.onSelectCountry(
                    calldata[1], calldata[2])
                bot.edit_message_text(
                    chat_id=update.effective_message.chat_id,
                    message_id=message.message_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            case 'country':
                offer, providers = SearchCommand.onOffer(
                    calldata[1], calldata[2], calldata[3])
                dictlist = SearchCommand.onOfferConvert(offer, providers)
                for i in dictlist:
                    text, reply_markup = SearchCommand.onOfferSender(
                        dictlist[i], i, calldata[1])
                    message = bot.send_message(
                        chat_id=update.effective_message.chat_id,
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    bot.edit_message_reply_markup(
                        chat_id=update.effective_message.chat_id,
                        message_id=message.message_id,
                        reply_markup=reply_markup,
                    )

    logging.info(f'{query.message.chat.id}@{query.message.chat.username} - {query.data}')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    updater = Updater('5477126979:AAH6Z9b5P5FqPjro_Kk6QJXPlUz97r9UJIY')

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("today", today))
    dispatcher.add_handler(CommandHandler('actor', actor))
    dispatcher.add_handler(CommandHandler('acts', acts))
    dispatcher.add_handler(CommandHandler('acts_ar', acts_ar))
    dispatcher.add_handler(InlineQueryHandler(inline_search))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, search))
    dispatcher.add_handler(MessageHandler(Filters.all, message_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
