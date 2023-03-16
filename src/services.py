"""A module that consists of the services that could be used in business process.

Basically it tries to separate layer of the library and provide generic API,
so that the underlying library could easily be changed.

Usage:
    import services
    city: models.CityLocationDataclass
    city = services.search_city("New York")
"""

import logging

from typing import List, Generator
from datetime import datetime

import pycountry

import config
import random
import messages
import exceptions

from lib import models, hotels, geocoding, exceptions as lib_exceptions


HOTEL_CLIENT = hotels.HotelsAPI(api_key=config.RAPIDAPI_TOKEN)
GEOCODING_CLIENT = geocoding.GeocodingAPI(api_key=config.RAPIDAPI_TOKEN)

META_DATA = HOTEL_CLIENT.get_meta_data()


logger = logging.getLogger("services")

def search_city(city: str) -> models.CityLocationDataclass:
    """Searches for a city in a geocoding API.

    It searches for the full information from the user-put city name.

    Args:
        city: a user-provided city name to be tried in searching for

    Returns:
        a dataclass representing a full information of the found city

    Raises:
        exceptions.CityNotFoundException: if city was not found
    """
    cities_alike = GEOCODING_CLIENT.forward_geocoding(city)
    cities_alike = sorted(cities_alike, key=lambda loc: loc.importance)
    try:
        found_city = cities_alike[0]
    except IndexError as e:
        raise exceptions.CityNotFoundException from e
    return found_city


def search_hotels_city(city: models.LocationDataclass) -> models.LocationDataclass:
    """Searches for hotels API specific city.

    As long as hotels.com may not know about a certain city that we would like
    to get properties from, we need to query and find a city in the hotels api.

    Args:
        city: a dataclass that represents all the information about a city(or a location)

    Returns:
        a dataclass that represents a found location(city) from the hotels api

    Raises:
        exceptions.AmbigousCityException: if there were multiple cities found from the queried one
    """

    locations = HOTEL_CLIENT.search_locations(city.name)
    locations = list(filter(lambda loc: loc.type == models.LocationTypeEnum.city, locations))

    if len(locations) > 1:
        for location in locations:
            if location.name == city.name:
                return location
        raise exceptions.AmbigousCityException

    return locations[0]


def search_hotels(
        city: models.CityLocationDataclass, 
        hotels_count: int, 
        photos_count: int,
        check_in: datetime,
        check_out: datetime,
        filters: List[models.SearchFilter],
        max_distance_downtown: float,

        rooms=hotels.HotelsRooms(adults=1),
        currency=models.EnumCurrency.USD,
        locale=models.EnumLocale.en_GB,
        sort=hotels.EnumHotelsSort.price_asc,
        sort_function=sorted,

        result_offset=0,
        result_limit=20,

        ) -> Generator[models.PropertyDataclass, None, bool]:
    """Searches for the hotels from the hotels API and yields them.

    It's the mainly used method that is used to search hotels from the 
    hotels API.

    Args:
        city: a string that represents a user-requested city to search hotels for
        hotels_count: an amount of hotels to search for
        photos_count: an amount of how many photos to include into the response
        check_in: a datetime object that represents an information of a desired check-in date
        check_out: a datetime object that represents an information of a desired check-out date

        filters: a list of search filters to be used in a query
        max_distance_downtown: a float that represents a maximum distance
        in kilometers to retrieve hotels within

        rooms: a dataclass that represents hotels-specific persons amount to search hotels with
        currency: a currency that should be used to return price with
        locale: a locale to be used to return string info with
        sort: a hotels-specific sorting types to be used in a query
        result_offset: an offset from which to start search from
        result_limit: amount of hotels to retrieve in one query

    Note:
        that this is a generator, it yields info one-by-one
    """


    destination = search_hotels_city(city)
    logger.debug(destination)
    destination = hotels.HotelsDestinationRegionID.from_location_dataclass(destination)
    logger.debug(destination)

    check_in = hotels.HotelsCheckpoint.from_datetime(check_in)
    check_out = hotels.HotelsCheckpoint.from_datetime(check_out)

    filters = [hotels.generic_search_filter_adapter(filter_) for filter_ in filters]
    payload = hotels.HotelsPropertySearchDataclass(
            currency=currency,
            locale=locale,
            destination=destination,
            check_in=check_in,
            check_out=check_out,
            rooms=rooms,
            result_offset=result_offset,
            result_limit=result_limit,
            sort=sort,
            filters=filters
            )
 
    logger.debug(payload.build_query_dict())
    properties = HOTEL_CLIENT.search_properties(payload)
    _filter_lambda = lambda prop: float(prop.distance_from_downtown.get_kilometers()) <= max_distance_downtown
    
    logger.debug(sort_function)
    properties = sort_function(properties)
    properties = filter(_filter_lambda, properties)
    for property in properties:
        property = HOTEL_CLIENT.update_property_with_info(property)
        yield property

    return properties

    
    
def build_message_from_property_dataclass(prop: models.PropertyDataclass):
    """Builds a string to send to the end user from the template.

    Args:
        prop: a dataclass representing property for which the messge would be built
    """

    return messages.HOTEL_MESSAGE_TEMPLATE.format(
            hotel_name=prop.name, 
            hotel_address=prop.address,
            hotel_distance_downtown=prop.distance_from_downtown,
            hotel_price=prop.price,
            hotel_link="https://www.hotels.com/h{0}.Hotel-Information".format(prop.id)
            )

def get_random_loading_message() -> str:
    """Returns a random progress loader message"""
    return random.choice(messages.LOADING_PROGRESS_MESSAGES)
