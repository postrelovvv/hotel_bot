"""A module that consists of all the base dataclass aka models, as well enums to use accross the lib.

The models here could be used internally by the library, as well as externally
to refer to the same entities across the project.
"""
from enum import Enum
from decimal import Decimal
from dataclasses import dataclass
from typing import List


class EnumCurrency(Enum):
    """Currency info.
    
    Consists of all the known currencies to be used.

    Attributes:
        USD: a tuple representing a short code of the currency and a full name
        RUB: a tuple representing a short code of the currency and a full name
    """

    USD = ("USD", "US Dollar")
    RUB = ("RUB", "Russian Ruble")


    def get_code(self):
        """Returns a code of the selected currency."""
        return self.value[0]

    def get_name(self):
        """Returns a name of the selected currency."""
        return self.values[1]

@dataclass
class Locale:
    """Locale info.

    Attributes:
        code: code of a locale in an ISO format, such as ru_RU, en_US and so on
        country: a string representing a country name
    """
    code: str
    country: str

class EnumLocale(Enum):
    """Enumeration of the known locales.

    Attributes:
        ru_RU: a locale that represents a russian locale
        en_GB: a locale that represents a british locale
    """
    ru_RU = Locale("ru_RU", "Russian")
    en_GB = Locale("en_GB", "British")

    def get_code(self):
        """Returns the code of the selected locale."""
        return self.value.code

class EnumDistanceUnit(Enum):
    """Enumeration of the known distance units.

    Attributes:
        Mile: an entity that represents a land-mile
        Kilometer: an entity that represents a kilometer
    """
    Mile = "MILE"
    Kilometer = "KILOMETER"

@dataclass
class DistanceDataclass:
    """Information about a distance in decimal and the unit.

    Attributes:
        distance: a decimal, or basically a float that represents value of the distance
        unit: a unit that is used to represent the distance value, such as mile
    """
    distance: Decimal
    unit: EnumDistanceUnit


    def __str__(self):
        """Returns a formatted string of the distance."""
        return "{0}{1}".format(self.distance, self.unit.value)

    def get_kilometers(self) -> Decimal:
        """Returns a distance in kilometers."""
        if self.unit is EnumDistanceUnit.Kilometer:
            return self.distance
        elif self.unit is EnumDistanceUnit.Mile:
            return self.distance * 1.60934

@dataclass
class PriceDataclass:
    """Information about a price.

    Attributes:
        price: a decimal value representing a value of the price
        currency: a selected currency from the enumeration that is used to represent a currency
    """
    price: Decimal
    currency: EnumCurrency

    def __str__(self):
        """Returns a formatted string with the price and its' code."""
        return "{0}{1}".format(float(self.price), self.currency.get_code())

@dataclass
class CoordinatesDataclass:
    """Coordinates information.

    Attributes:
        lat: an attribute that represents a latitude
        long: an attribute that represents a long
    """
    lat: Decimal
    long: Decimal


class LocationTypeEnum(Enum):
    """Type of a location.

    Represents a hotels' types of locations that could be found in search
    locations method.
    """
    city = "CITY"
    hotel = "HOTEL"
    neighborhood = "NEIGHBORHOOD"
    poi = "POI"
    airport = "AIRPORT"
    multiregion = "MULTIREGION"


@dataclass
class LocationDataclass:
    """Location info.

    Attributes:
        id: if of the location
        name: name of the location
        type: type of the location
        coordinates: coordinates that correspond to the location
    """
    id: int
    name: str
    type: LocationTypeEnum
    
    coordinates: CoordinatesDataclass

@dataclass
class CityLocationDataclass(LocationDataclass):
    """City location information.

    Inherits location dataclass and adds a new option about a country.

    Attributes:
        country: a string representing a country
    """
    country: str

@dataclass
class PropertyDataclass:
    """Property information.

    A dataclass that represents the whole information about a property.

    Attributes:
        id: unique identifier of the property
        name: a string represeting a name of the property
        price: a dataclass that has information about the price of the property
        distance_from_downtown: a distance dataclass that has information about
        the distance from the downtown to the property
        coordinates: a dataclass that represents coordinates of the property
    """
    id: int

    name: str
    price: PriceDataclass

    distance_from_downtown: DistanceDataclass
    coordinates: CoordinatesDataclass

    images_links: List[str] = None
    address: str = None



@dataclass
class SearchFilter:
    """Search filter."""
    pass

@dataclass
class PriceFilter(SearchFilter):
    """Price search filter."""
    max_price: int
    min_price: int


