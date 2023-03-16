"""A module that consists of all the messages that are used in the conversations."""
ASK_LOCATION_MESSAGE = "Напиши город для поиска отелей"
ASK_HOTELS_COUNT_MESSAGE = "Какое количество отелей грузить?"
ASK_LOAD_PHOTOS_MESSAGE = "Грузить фотки? Да/Нет"
ASK_PRICE_RANGE_MESSAGE = "Какой диапазон цен в долларах?\nПример: 100-150"
ASK_DISTANCE_DOWNTOWN_MESSAGE = "Какое максимальное расстояние до центра в километрах?"
ASK_CHECKIN_DATE_MESSAGE = "Напиши дату заезда в формате: мм.дд.гггг\nПример: 17.12.2002"
ASK_CHECKOUT_DATE_MESSAGE = "Напиши дату выезда в формате: мм.дд.гггг\nПример: 17.12.2002"

LOADING_PROGRESS_MESSAGES = (
        "🤖 Спрашиваем у отельеров...",
        "🤖 Переворачиваем весь Яндекс...",
        "🤖 Переходим по ссылкам...",
        "🤖 Дёргаем за ниточки...",
        )

STOP_MESSAGE = "Остановились..."
START_MESSAGE = "Приветствую! Выберите интересующую Вас команду."
HELP_MESSAGE = "Все доступные команды:\n/start - запустить бота\n/stop - остановить бота\n/help - поддерживаемые команды \
               \n/lowprice - топ дешёвых отелей\n/highprice - топ дорогих отелей \
               \n/bestdeal - топ отелей, наиболее подходящих по цене и расположению от центра"

HOTEL_MESSAGE_TEMPLATE = """📛 Название отеля: {hotel_name}
🏨 Адрес отеля: {hotel_address}
🚶 Расстояние до центра: {hotel_distance_downtown}
💰 Цена отеля за все дни: {hotel_price}
<a href="{hotel_link}">Ссылка</a>
"""
