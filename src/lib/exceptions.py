"""Module which describes common exceptions to be used across the library.

It's basically a module which has exceptions defined in one place and could
be shared accross the library to refer to exceptions.
"""

from typing import List

class RapidAPIException(Exception):
    """Base exception that represents an exception happened during handling
    an api request."""


class HotelsAPIException(RapidAPIException):
    """Base exception that represents an exception happened in during handling
    an api request in Hotels api."""


class CountryNotSupported(HotelsAPIException):
    """An exception represents that country is not supported by the API.

    Attributes:
        country_code: a string representing a code of country which is not supported
        message: full message containing formatted message of the exception
    """
    
    def __init__(self, country_code: str):
        """Init an exception instance with specific country code that
        is not supported.

        Args:
            country_code: a string representing an ISO code of country which
                is not supported by the HotelsAPI
        """
        self.country_code = country_code

        self.message = "Country with code {0} is not supported".format(self.country_code)
        super().__init__(self.message)


class AmbigousCityException(HotelsAPIException):
    """An exception represents that there were multiple cities to choose from.

    It's possible that on a request to the api, that there would be multiple
    cities to choose from. Hence the exception is raised.

    Attributes:
        message: a formatted message with the exception containing
            locations(cities) that were found and were unable to be distincted

        locations: list of locations(models.LocationDataclass) representing
            locations that were found, but were unable to be distincted which
                one to use
    """
    
    def __init__(self, locations: List['models.LocationDataclass']):
        """Init an exception with locations list that were unable to be used.

        Args:
            locations: list of models.LocationDataclass that were found during
                a search request
        """
        self.message = "Ambigous city to choose {0}".format(locations)
        self.locations = locations

        super().__init__(self.message)


