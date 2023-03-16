"""A module that consists of all the bot-spaced exceptions."""

class BotException(Exception):
    pass


class BotValidationException(BotException):
    pass


class CityNotFoundException(BotValidationException):
    """City not found with a given name."""

    message = "Город с таким именем не найден"


class AmbigousCityException(BotValidationException):
    """Multiple cities were found with the given name."""

    message = "С таким названием найдено несколько городов. Попробуйте уточнить поиск."


class CityCountryNotSupportedException(BotValidationException):
    """Country of a city is not supported."""

    message = "Страна предоставленного города не поддерживается."


class WrongTextMessageFormatException(BotValidationException):
    pass

class NotNumericValueException(WrongTextMessageFormatException):
    """A value that was provided is not a numeric or not convertible to one."""

    message = "Не числовое значение."

class NotZeroValueException(BotValidationException):
    """A value that was provided is a zero."""

    message = "Число не может быть нулём или меньше нуля."

class WrongDateFormatException(WrongTextMessageFormatException):
    """A string is not in compliance with a format."""

    message = "Неверный формат даты."


class WrongPriceRangeFormatException(WrongTextMessageFormatException):
    """Wrong price range format provided from the user."""

    message = "Неверный формат ценового диапазона."

class PriceRangeFirstIsBiggerThanSecond(WrongTextMessageFormatException):
    """Second value of a price range is less than the first one."""

    message = "Второе число ценового диапазона не может быть меньше первого или равно."


class WrongBooleanMessageFormatException(WrongTextMessageFormatException):
    """The user-input string is not in compliance with a pre-defined boolean answers."""

    message = "Неверный формат ответа."


class WrongDateProvidedException(BotValidationException):
    pass


class PastDateProvidedException(WrongDateProvidedException):
    """A date that was provided is in the past."""

    message = "Дата не может быть в прошлом или равна текущему дню."


class EndDateLessThanStartDateException(WrongDateProvidedException):
    """A check-out date that was provided is before check-in."""
    message = "Дата выезда не может быть раньше/равна датe заезда."


