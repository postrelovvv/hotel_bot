import os
import enum
import json
import logging
from datetime import datetime

import pycountry

from telegram import Update, InputMediaPhoto
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from telegram.ext import (
        ApplicationBuilder, 
        ContextTypes, 
        CommandHandler, 
        MessageHandler,
        ConversationHandler,
        filters
        )

import config
import messages
import services
import validators
import enums
import exceptions

from lib import models

# NOTICE: models should be generic, probably move models to some other place
# the main catch here is to do not use any implementation of the lib, but
# our own of the bot, and adapt it


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger("main")



async def deals_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    command = enums.DealsCommandTypeEnum(update.message.text.replace("/", ""))
    context.user_data["sort_function"] = enums.HotelsSorterFunctionsEnum.from_deals_command_type(command)
    logger.debug(context.user_data)
    await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=messages.ASK_LOCATION_MESSAGE,
            )

    return enums.StatesEnum.LOCATION


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = services.search_city(update.message.text)
    validators.validate_country_supported_from_city(city)
    city = services.search_hotels_city(city)
    context.user_data["city"] = city


    await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=messages.ASK_CHECKIN_DATE_MESSAGE
            )

    return enums.StatesEnum.CHECKIN

async def handle_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    check_in = validators.validate_date(update.message.text)
    validators.validate_date_has_not_past(check_in)

    context.user_data["check_in"] = check_in

    await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=messages.ASK_CHECKOUT_DATE_MESSAGE,
            )

    return enums.StatesEnum.CHECKOUT

async def handle_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    check_out = validators.validate_date(update.message.text)
    check_in = context.user_data["check_in"]
    validators.validate_checkout_date_is_past_checkin(check_in, check_out)

    context.user_data["check_out"] = check_out
    await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=messages.ASK_HOTELS_COUNT_MESSAGE
            )

    return enums.StatesEnum.HOTELS_COUNT


async def handle_hotels_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hotels_count = validators.validate_float(update.message.text)
    if hotels_count <= 0:
        raise exceptions.NotZeroValueException

    context.user_data["hotels_count"] = hotels_count

    await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=messages.ASK_PRICE_RANGE_MESSAGE,
            )

    return enums.StatesEnum.PRICE_RANGE

async def handle_price_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price_range"] = validators.validate_price_range(update.message.text)

    await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=messages.ASK_DISTANCE_DOWNTOWN_MESSAGE
            )

    return enums.StatesEnum.MAX_DISTANCE_DOWNTOWN

async def handle_distance_downtown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    distance_downtown = validators.validate_float(update.message.text)

    if distance_downtown <= 0:
        raise exceptions.NotZeroValueException

    context.user_data["distance_downtown"] = distance_downtown

    await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=messages.ASK_LOAD_PHOTOS_MESSAGE,
            )
    

    return enums.StatesEnum.LOAD_PHOTOS

async def handle_load_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data["load_photos"] = validators.validate_bool_answer(update.message.text)

    message = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=services.get_random_loading_message()
            )

    await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=str(context.user_data)
            )
    
    city = user_data["city"]
    hotels_count = user_data["hotels_count"]

    check_in = user_data["check_in"]
    check_out = user_data["check_out"]
    min_price, max_price = user_data["price_range"]
    load_photos = user_data["load_photos"]
    max_distance_downtown = user_data["distance_downtown"]
    sort_function = user_data["sort_function"]

    _filters = [models.PriceFilter(min_price=min_price, max_price=max_price)]
    hotels_d = services.search_hotels(
            city=city,
            hotels_count=hotels_count,
            max_distance_downtown=max_distance_downtown,
            photos_count=hotels_count,
            check_in=check_in,
            check_out=check_out,
            filters=_filters,
            sort_function=sort_function.value,
            result_limit=hotels_count,
            )


    async def send_plain_message(bot, property):
        property_message = services.build_message_from_property_dataclass(hotel)
        logger.debug(property_message)
        return await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=property_message,
            parse_mode=ParseMode.HTML
            )


    
    async def send_mediagroup(bot, property, amount=3):
        property_message = services.build_message_from_property_dataclass(hotel)
        media_group = []
        for i, image_link in enumerate(property.images_links):
            if i > amount:
                break
            media_group.append(InputMediaPhoto(image_link))
        logger.debug(media_group)

        return await bot.send_media_group(
                chat_id=update.effective_chat.id, 
                media=media_group,
                parse_mode=ParseMode.HTML,
                caption=property_message
                )


    send_message_func = send_mediagroup if load_photos else send_plain_message

    for hotel in hotels_d:
        await send_message_func(context.bot, hotel)
        
    return ConversationHandler.END


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(
            msg="Exception happened during handling an update:", 
            exc_info=context.error
            )

    await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=context.error.message
            )

async def stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=messages.STOP_MESSAGE
    )
    return ConversationHandler.END

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=messages.START_MESSAGE
    )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=messages.HELP_MESSAGE
    )

if __name__ == "__main__":

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    just_text_filter = filters.TEXT & (~ filters.COMMAND)
    deals_commands = enums.DealsCommandTypeEnum.as_commands_list()
    logger.debug(deals_commands)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(deals_commands, deals_handler)],
        states={
            enums.StatesEnum.LOCATION: [MessageHandler(just_text_filter, handle_location)],
            enums.StatesEnum.HOTELS_COUNT: [MessageHandler(just_text_filter, handle_hotels_count)],
            enums.StatesEnum.CHECKIN: [MessageHandler(just_text_filter, handle_checkin)],
            enums.StatesEnum.CHECKOUT: [MessageHandler(just_text_filter, handle_checkout)],
            enums.StatesEnum.PRICE_RANGE: [MessageHandler(just_text_filter, handle_price_range)],
            enums.StatesEnum.MAX_DISTANCE_DOWNTOWN: [MessageHandler(just_text_filter, handle_distance_downtown)],
            enums.StatesEnum.LOAD_PHOTOS: [MessageHandler(just_text_filter, handle_load_photos)],
        },
        fallbacks=[CommandHandler(deals_commands, deals_handler), CommandHandler("stop", stop_handler)],
    )
    start_handler = CommandHandler("start", start_handler)
    help_handler = CommandHandler('help', help_handler)
    app.add_handler(help_handler)
    app.add_handler(start_handler)
    app.add_handler(conv_handler)
    app.add_error_handler(error_handler)

    app.run_polling()


