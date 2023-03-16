"""A module that consists of all the validators needed for the user-input."""

from typing import List
from datetime import datetime

import pycountry
from lib import  models

import exceptions
import consts
import services


def validate_float(text: str) -> float:
    """Validates that the input string is convertable to float and returns it.

    Args:
        text: a string to validate for being a float

    Returns:
        a float number if the validation was succesful

    Raises:
        exceptions.NotNumericValueException: if the provided value is not convertible to a float
    """
    try:
        return float(text)
    except ValueError as e:
        raise exceptions.NotNumericValueException from e


def validate_date(text: str, format_=consts.DATE_FORMAT) -> datetime:
    """Validates that string is a date with the right format.

    Args:
        text: a user-input text that consists of a date with a compliance to a format
        format_: a format that the given text string should comply with

    Returns:
        a datetime object if a validation was successful

    Raises:
        exceptions.WrongDateFormatException: if the format of a given string was wrong
    """
    try:
        return datetime.strptime(text, format_)
    except ValueError as e:
        raise exceptions.WrongDateFormatException from e


def validate_date_has_not_past(date: datetime):
    """Validates that a date is not in the past.

    Args:
        date: a datetime object to validate

    Raises:
        exceptions.PastDateProvidedException: if date is in the past
    """

    now = datetime.now()
    if date <= now:
        raise exceptions.PastDateProvidedException

def validate_checkout_date_is_past_checkin(
        date_checkin: datetime, 
        date_checkout: datetime
        ):
    """Validates that the check-out date is after the check-in date.

    Args:
        date_checkin: a datetime object of supposed check-in
        date_checkout: a datetime object of supposed check-out

    Raises:
        exceptions.EndDateLessThanStartDateException: if the check-out date is before the check-in
    """


    if date_checkout <= date_checkin:
        raise exceptions.EndDateLessThanStartDateException

def validate_price_range(
        text: str, 
        format_=consts.PRICE_RANGE_FORMAT_RE,
        separator=consts.PRICE_RANGE_SEPARATOR
        ) -> List[float]:
    """Validates that a given price range is valid, and if so returns it.

    Args:
        text: a string representing a price range
        format_: a separator to separate given text to obtain values with

    Returns:
        first and second value of a given price range

    Raises:
        exceptions.WrongPriceRangeFormat: if the format of the given range is invalid
        exceptions.NotZeroValueException: if the second value obtained from 
        the price range is a zero or less, as well as the first one being less than zero
        exceptions.PriceRangeSecondIsBiggerThanFirst: if the first value of 
        a given price range is bigger than the second
    """
    if not consts.PRICE_RANGE_FORMAT_RE.match(text):
        raise exceptions.WrongPriceRangeFormatException

    separator = consts.PRICE_RANGE_SEPARATOR
    try:
        first, second = [float(piece) for piece in text.split(separator)]
    except ValueError as e:
        raise exceptions.WrongPriceRangeFormatException from e
    else:
        if second <= 0 or first < 0:
            raise exceptions.NotZeroValueException
        if second <= first:
            raise exceptions.PriceRangeSecondIsBiggerThanFirst

        return first, second


def validate_country_supported_from_city(city: models.CityLocationDataclass):
    """Validates that a country of a city is supported by the hotels api.

    Args:
        city: a dataclass representing information about a city

    Raises:
        exceptions.CityCountryNotSupportedException: if a country is not supported
    """
    country_from_city = city.country
    country = pycountry.countries.search_fuzzy(country_from_city)[0]

    try:
        country_code = country.alpha_2
        hotels_country_info = services.META_DATA[country_code]
    except KeyError as e:
        raise exceptions.CityCountryNotSupportedException(country_code) from e


def validate_bool_answer(text: str) -> bool:
    """Validate that an answer is a boolean(either yes or no).

    Args:
        text: a string representing either yes or no

    Raises:
        exceptions.WrongBooleanMessageFormatException: if neither yes, nor no
    """
    text = text.strip()
    try:
        return consts.BOOL_ANSWER[text.lower()]
    except KeyError as e:
        raise exceptions.WrongBooleanMessageFormatException from e


