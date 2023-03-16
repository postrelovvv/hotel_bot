"""Module that provides a class and dataclasses to interact with Hotels.com API.

It consists of a class and dataclasses used exclusively with interacting with
the hotel.com api. A few utils functions that provide parsing routines of the
responses of the api.

Usage:
    from lib import hotels
    hotels_client = HotelsAPI(api_key="RAPID_API_KEY")
    locations: models.LocationDataclass
    locations = hotels_client.search_locations("New York")

"""

import logging
from typing import List, Dict
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
from collections import ChainMap
from datetime import datetime

from lib import models
from base import api

logger = logging.getLogger('api')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


def _parse_location_into_dataclass(location: dict) -> models.LocationDataclass:
    """Parses single entity from the list of entities returned from the API."""

    id_ = location['gaiaId']
    name = location['regionNames']['primaryDisplayName']
    type_ = models.LocationTypeEnum(location['type'])
    lat = Decimal(location['coordinates']['lat'])
    long = Decimal(location['coordinates']['long'])
    
    coordinates = models.CoordinatesDataclass(lat=lat, long=long)
    location_d = models.LocationDataclass(
            id=id_, 
            name=name, 
            coordinates=coordinates,
            type=type_,
            )

    return location_d


def _parse_locations_response_into_dataclasses(response: dict) -> List[models.LocationDataclass]:
    """Gets the list of entities returned from the API and parses each of those into a list"""

    response = response['sr']
    ret = []

    for location in response:
        logger.debug(location)
        try:
            location_d = _parse_location_into_dataclass(location)
        except KeyError:
            continue
        ret.append(location_d)

    return ret

       

@dataclass
class HotelsDestination:
    """A base dataclass to be used in search of a destination."""
    pass

@dataclass
class HotelsDestinationCoordinates(HotelsDestination):
    """Dataclass that provides a store for coordinates and function to build a query.

    Mainly its supposed to be used with search_properties of HotelsAPI and that
    should call build_query_dict to create an API specific dict to query it

    Attributes:
        coordinates: a coordinates dataclass that holds info about coordinates
            to be used in search locations of the hotels api
    
    Note:
        its worth noting that coordinates in the api are optional, they can't
        be used to just substitute search by regionId(gaiaId of the city),
        it could only be used in conjunction with regionId search to kind of
        precise the coordinates of where you would like to query properties from
    """
    coordinates: models.CoordinatesDataclass

    def build_query_dict(self):
        """Builds a dict to be used in search for properties queries.

        Returns:
            a dict containing two keys which represent coordinates of the
            location to search properties around from
        """

        return {
                "latitute": self.coordinates.lat, 
                "longtitute": self.coordinates.long
                }

@dataclass
class HotelsDestinationRegionID(HotelsDestination):
    """Id of the location to search properties from.

    Attributes:
        id: an integer which is gaiaId returned from the search_locations API

    Note:
        required to be used in search_properties API query as long as its
            mandatory in a api definition
    """
        
    id: int

    def build_query_dict(self) -> dict:
        """Builds a query dict to be used in an API call.

        Returns:
            returns a dict containing an id of the region to search for
        """

        return {"regionId": str(self.id)}

    @classmethod
    def from_location_dataclass(cls, location_d: models.LocationDataclass):
        """Creates an instance of the dataclass from a LocationDataclass.

        Returns:
            returns an instance of the dataclass from the LocationDataclass
        """
        return cls(location_d.id)

@dataclass
class HotelsCheckpoint:
    """Date of either a check in or check out to search hotels for.

    Basically holds info about when the check in or check out dates could occur
    from the customer perspective.

    Attributes:
        day: an integer representing a day within a month 0-31
        month: an integer representing a month of a year 1-12
        year: an integer representing a year

    Note:
        values of a dataclass to be populated are not validated, means that it
        just stores info, you have to validate info yourself before puting
        it into the dataclass
    """
    day: int
    month: int
    year: int

    def build_query_dict(self) -> dict:
        """Builds a query dict to be used in search of properties API query.

        Returns:
            a dict containing dataclass attributes as keys and values of those
            in values

        Note:
            the return model is not strictly set, it will change on any new
            attribute added to the dataclass. Make sure to maintain the current
            protocol and convention of the attributes of this dataclass.
            Otherwise you would get either an error from the API, or you would
            get invalid responses from the API.
        """

        return self.__dict__

    @classmethod
    def from_datetime(cls, datetime_: datetime):
        """Creates an instance of the dataclass from datetime object.

        Args:
            datetime_: a datetime object that should hold info about a
                day, month and a year

        Returns:
            an instance of the dataclass
        """

        return cls(
                day=datetime_.day, 
                month=datetime_.month, 
                year=datetime_.year
                )

@dataclass
class HotelsRooms:
    """Count of rooms for adults and children.

    For now it stores info about count of adults that are going into some hotel.
    And is used when searching for properties to define how many humans would be
    living in a property.

    Attributes:
        adults: amount of adults that would be living in a property

    Note:
        its also possible to implement holding info about how many children
        would be there.
    """
        
    adults: int

    # children could be implemented here as well

    def build_query_dict(self):
        """Creates a dictionary to be used in searching for property.

        Returns:
            a list of of human types and their amount that are going to live
            in a property, for now only one element containing info about adults
        """
        return [self.__dict__]


class EnumHotelsSort(Enum):
    """Sorting options for the API.

    Contain all the possible sorting options available through the API.

    Attributes:
        price_asc: sorting by price ascending
        price_relevant: sorting by price ascending(?) and platform recommendations
        review: sort by by guest rating descending(?)
        distance: sort by distance descending(?)
        stars: sort by count of hotel stars descending(?)
        recommended: sort by the recommendations of the platform

    Note:
        its unclear from the API definition either some sorting options
        are ascending or descending, its worth a manual try to understand it
    """
    price_asc = "PRICE_LOW_TO_HIGH"
    price_relevant = "PRICE_RELEVANT"
    review = "REVIEW"
    distance = "DISTANCE"
    stars = "PROPERTY_CLASS"
    recommended = "RECOMMENDED"


    def __str__(self):
        """Returns a value selected attribute to be used in API sorting."""
        return self.value


@dataclass
class HotelsFilter:
    """Filter to be used in searching for property"""
    pass


@dataclass
class HotelsPriceFilter(HotelsFilter, models.PriceFilter):
    """Filter by price in the API.

    Its derived from the base price filter and is meant to be used when filtering
    out the price by the minimum and maximum range.

    Attributes:
        max_price: holds info about a maximum price of the property(a hotel) to seek for
        min_price: holds info about a minimum price of the property(a hotel) to seek for
    """

    def build_query_dict(self):
        """Builds a query dict to be used in API search for properties call."""
        return {"price": {"max": float(self.max_price), "min": float(self.min_price)}}

    @classmethod
    def from_generic_price_filter(cls, filter_: models.PriceFilter):
        """Creates an instance of this dataclass from the generic price filter."""
        return cls(**filter_.__dict__)


def generic_search_filter_adapter(filter_: models.SearchFilter) -> HotelsFilter:
    """Adapter/factory to create hotels specific filters from a base dataclasses.

    Args:
        filter_: a base dataclass for a filter from a models module

    Raises:
        ValueError: if no adapters were found for the provided filter dataclass
    """

    if isinstance(filter_, models.PriceFilter):
        return HotelsPriceFilter.from_generic_price_filter(filter_)

    raise ValueError("{0} filter no adapter found".format(filter_))


class EnumHotelsRating(Enum):
    """Hotels guest rating as defined in the API definition.

    Attributes:
        good: 7+ in the hotels.com filters
        very_good: 8+ in the hotels.com filters
        wonderful: 9+ in the hotels.com filters

    """
    good = 35
    very_good = 40
    wonderful = 45


@dataclass
class HotelsRatingFilter(HotelsFilter):
    """Hotels rating filter to be used in API query.

    Attributes:
        rating: a rating from the defined API of the hotels.com
    """
    rating: EnumHotelsRating


    def build_query_dict(self):
        """Builds a dict to be used in search for properties filters.

        Returns:
            a dict containing a key guestRating and the respective rating value
        """
        return {"guestRating": self.rating}

@dataclass
class HotelsCountryInfoDataclass:
    """Information about a country.

    Attributes:
        code: ISO country code (see IBM definition)
        site_id: and internal hotels' site_id
        tpid: an internal id of the hotels
        eapid: optional id that stores an internal id of hotels API

    Note:
        eapid is optional for a reason, some countries may not have it for
        some reason, but it could be used when searching for the properties
        and locations
    """
    code: str
    site_id: int
    tpid: int

    eapid: int = None


@dataclass
class HotelsPropertySearchDataclass:
    """Information about the search query for properties.


    Attributes:
        currency: currency as a short code
        locale: ISO locale. E.g: ru_RU, en_US, en_GB, ...
        destination: info about a destination. Usually being a regionid
        check_in: info about the desired time of a checkin into the hotel
        check_out: info about a desired time of a checkout out of the hotel
        rooms: rooms that are needed for specific-aged people as defined in HotelsRooms
        filters: a list of hotels-specific filters to be used in a search query
        sort: sort by chosen from the available sorting options from the Enum
        result_offset: a result offset to start search from. Could be used for pagination purposes
        result_limit: a limit how many results to get from the API
    """

    currency: models.EnumCurrency
    locale: models.EnumLocale
    destination: HotelsDestination
    check_in: HotelsCheckpoint
    check_out: HotelsCheckpoint
    rooms: HotelsRooms
    filters: List[HotelsFilter]
    sort: EnumHotelsSort

    result_offset: int = 0
    result_limit: int = 50

    def build_query_dict(self) -> dict:
        """Build a query dict needed for the search for properties API.

        Uses a utility function to generate a dict(JSON) query for the search
        for properties api.

        Returns:
            a dict that should be used for querying the API
        """

        return _build_payload_for_hotels_search(
                currency=self.currency,
                locale=self.locale,
                destination=self.destination,
                check_in=self.check_in,
                check_out=self.check_out,
                rooms=self.rooms,
                filters=self.filters,
                sort=self.sort,
                result_offset=self.result_offset,
                result_limit=self.result_limit
                )


def _parse_property_into_dataclass(prop: dict) -> models.PropertyDataclass:
    """Utility function to parse gotten property into the appropriate dataclass."""
    id_ = prop["id"]
    name = prop["name"]

    currency = getattr(
            models.EnumCurrency, 
            prop["price"]["lead"]["currencyInfo"]["code"]
            )

    price_d = models.PriceDataclass(
            price=prop["price"]["lead"]["amount"],
            currency=currency
            )
    distance = prop["destinationInfo"]["distanceFromDestination"]["value"]
    unit = prop["destinationInfo"]["distanceFromDestination"]["unit"]

    distance_from_downtown_d = models.DistanceDataclass(
            distance=distance, 
            unit=models.EnumDistanceUnit(unit)
            )
    coordinates_d = models.CoordinatesDataclass(
            lat=prop["mapMarker"]["latLong"]["latitude"],
            long=prop["mapMarker"]["latLong"]["longitude"]
            )

    property_d = models.PropertyDataclass(
            id=id_,
            name=name, 
            price=price_d, 
            distance_from_downtown=distance_from_downtown_d,
            coordinates=coordinates_d
            )

    return property_d

def _parse_properties_response_into_dataclasses(
        response: dict
        ) -> List[models.PropertyDataclass]:
    """Utility function to parse response of properties into the list of dataclasses."""
        
    properties = response['data']['propertySearch']['properties']

    ret = []
    for prop in properties:
        
        property_d = _parse_property_into_dataclass(prop)
        ret.append(property_d)

    return ret


def _create_dataclass_from_country_info(
        country_code: str, 
        info: dict
        ) -> HotelsCountryInfoDataclass:
    """A utility function that creates a country dataclass.

    Args:
        country_code: ISO country code such as AE, KZ, RU, US, ...
        info: a dict containing api specific info

    """

    return HotelsCountryInfoDataclass(
            code=country_code, 
            site_id=info['siteId'],
            eapid=info.get("EAPID", None),
            tpid=info['TPID']
            )

def _parse_countries_into_dataclasses(
        response: dict
    ) -> Dict[str, HotelsCountryInfoDataclass]:
    """A utility function that parses response into the dict of countries.

    Args:
        response: a dict containing a response from a meta info API query.

    Returns:
        a dict where the key is a country code in a ISO format and values as
        a country info dataclass
    """

    ret = {}
    for country_code, info in response.items():
        ret[country_code] = _create_dataclass_from_country_info(
                country_code, 
                info
                )
    return ret
 

def _build_payload_for_hotels_search(
        currency: models.EnumCurrency,
        locale: models.EnumLocale,
        destination: HotelsDestination,
        check_in: HotelsCheckpoint,
        check_out: HotelsCheckpoint,
        rooms: HotelsRooms,
        result_offset: int,
        result_limit: int,
        sort: EnumHotelsSort,
        filters: List[HotelsFilter]

        ):
    """A utility function that builds a dictionary to query properties search API.

    Args:
        currency: a chosen currency as defined in models.EnumCurrency, basically
        a USD, RUB, or as such

        locale: a locale chosen from the models.EnumLocale, basically an ISO
        formatted string such as ru_RU, en_US, en_GB and so on

        destination: a destination chosen from the HotelsDestination enum,
        almost always would be a region id destination as long as it's
        mandatory by the API definition

        check_in: a desired check-in date as a HotelsCheckpoint dataclass
        check_out: a desired check-out date as a HotelsCheckpoint dataclass
        rooms: information about the persons that are going to stay in the hotel,
        mainly its just an amount of adults or children and their ages afaik
        
        result_offset: a result offset that would be used to query hotel from
        result_limit: amount of results to get basically, a limit
        sort: chosen sorting type as defined in the API, and selected from a EnumHotelSort
        filters: list of HotelsFilter to be included in the search query

    Returns:
        a dict prepared to be used in search_properties gateway

    Note:
        the function uses ChainMap from collections, it could be misleading
        but the thing that particularly here it does, is just basically
        getting the built queries from the filters and putting them altogether
        in a single dict.
    """
    filters = [filter_.build_query_dict() for filter_ in filters]
    payload = {
            "currency": currency.get_code(),
            "locale": locale.get_code(),
            "destination": destination.build_query_dict(),
            "checkInDate": check_in.build_query_dict(),
            "checkOutDate": check_out.build_query_dict(),
            "rooms": rooms.build_query_dict(),
            "resultsStartingIndex": result_offset,
            "resultsSize": result_limit,
            "sort": str(sort),
            "filters": dict(ChainMap(*filters))
            }

    return payload

def _update_property_with_address(response: dict, property: models.PropertyDataclass):
    """Updates property address from the /details/ response from hotels api.

    Note:
        updates the original property dataclass as an intended effect
    """
    address = response["data"]["propertyInfo"]["summary"]["location"]["address"]["addressLine"]
    property.address = address
    return property


def _update_property_with_images_links(response: dict, property: models.PropertyDataclass):
    """Updates property images links from the /details/ response from hotels api.

    Note:
        updates the original property dataclass as an intended effect
    """
    images = response["data"]["propertyInfo"]["propertyGallery"]["images"]
    property.images_links = []
    for image in images:
        property.images_links.append(image["image"]["url"])
    return property



def _update_property_with_data(response: dict, property: models.PropertyDataclass):
    """Updates property with the /details/ data.

    Note:
        updates the original property dataclass as an intended effect
    """
    _update_property_with_address(response, property)
    _update_property_with_images_links(response, property)

    return property


class HotelsAPI(api.RapidAPIBase):
    """Provides methods to interact with hotels.com API from RapidAPI.

    Attributes:
        locale: a string representing a locale to be used in searches in ISO format
        e.g: en_US, ru_RU, en_GB, and so on

        currency: a currency to be used in return from the APIs calls, e.g: USD, RUB, ...

        base_url: a base url that would be added into every request
        host: a host that is needed for the RapidAPI to distinguish where to route request to
    """
    locale = "en_US"
    currency = "USD"

    base_url = "https://hotels4.p.rapidapi.com"
    host = "hotels4.p.rapidapi.com"

    def __init__(self, api_key: str):
        """Init the class with api key and api host from the class definition."""
        super().__init__(api_key=api_key, api_host=self.host)

    def update_property_with_info(self, prop: models.PropertyDataclass) -> models.PropertyDataclass:
        """Obtains info about a property from its' id and adds additional info.

        Some info such as images and address is not being listed in the
        /v2/list/ API call, and thus that info should be obtained through this
        API call

        Args:
            prop: a dataclass that represents a property

        Note:
            it updates the original property
        """
        url = "{0}/properties/v2/detail".format(self.base_url)
        payload = {
                "currency": prop.price.currency.get_code(),
                "locale": self.locale,
                "propertyId": prop.id
                }
        r = self._session.post(url, json=payload)

        return _update_property_with_data(response=r.json(), property=prop)



    def search_properties(
            self, 
            search_dataclass: HotelsPropertySearchDataclass
            ) -> List[models.PropertyDataclass]:
        """Searches for properties listed in the hotels.com.

        This method gets the information about the properties that could be
        checked in furtherly by the persons that are searching for properties.

        Args:
            search_dataclass: a dataclass that consists all the filled info
            about the search such as dates, price filter, amount of persons
            and so on
        """

        url = "{0}/properties/v2/list".format(self.base_url)
        r = self._session.post(url, json=search_dataclass.build_query_dict())

        return _parse_properties_response_into_dataclasses(r.json())


    def search_locations(
            self, 
            query: str,
            locale: str = None
            ) -> List[models.LocationDataclass]:
        """Gets all the locations(cities, hotels) for the given query.

        This is quite counter-intuitive, but locations could be not only
        cities, parks, point of views but also hotels. Mainly this method
        is used to get cities locations specific for the hotels API, and then
        obtained info about in consequent properties searches.

        Args:
            query: a string representing a location to search for, for example: New York, Dallas, ...
            locale: an ISO locale to be used in response such as ru_RU, en_GB, en_US
        """

        if locale is None:
            locale = self.locale

        url = "{0}/locations/v3/search".format(self.base_url)
        r = self._session.get(url, params={"q": query, "locale": locale})

        logger.debug(r.json())
        return _parse_locations_response_into_dataclasses(r.json())


    def get_meta_data(self) -> Dict[str, HotelsCountryInfoDataclass]:
        url = "{0}/v2/get-meta-data".format(self.base_url)
        logger.debug(url)
        r = self._session.get(url)

        return _parse_countries_into_dataclasses(r.json())



