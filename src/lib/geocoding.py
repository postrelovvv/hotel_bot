"""Module consists of a class that interacts with Forward & Reverse Geocoding API.

This module contains functions and class that are wrappers around a 
Forward & Reverse Geocoding API from Rapid.

Usage:
    from lib import geocoding
    geocoding_client = geocoding.GeocodingAPI("your rapid api key")
    city: models.CityLocationDataclass
    city = geocoding_client.forward_geocoding("New York")

"""

import logging

from typing import List
from dataclasses import dataclass

from lib import models
from base import api


logger = logging.getLogger("geocoding")

@dataclass
class GeocodingLocationDataclass(models.CityLocationDataclass):
    """A data store derived from models.CityLocationDataclass to store API specific data.

    Attributes:
        id - a unique identifier of a city specific for the geocoding API.
        name - a human-readable name of the city with country stripped. E.g: Dallas.
        type - a type of location, always models.LocationTypeEnum.city in this case.
        coordinates - a coordinates of a city retrieved from the API.
        country - a string representing a country name of a city. E.g United States
        importance - an API specific field which represents confidence about the
            query

    """

    importance: float


def _parse_locations_from_geocoding(response: dict):
    """Parses a response from geocoding api.

    Pretty basic function which just unfolds info from the JSON response of
    an API and puts everything into the GeocodingLocationDataclass.

    Args:
        response: a JSON(dict) response gotten from the forward geocoding api call
    Returns:
        a list of GeocodingLocationDataclass
    """

    ret = []
    for location in response:
        id = location['place_id']
        name, *_, country = location['display_name'].split(",")
        name, country = name.strip(), country.strip()
        lat = location['lat']
        long = location['lon']
        importance = float(location['importance'])

        coordinates = models.CoordinatesDataclass(lat=lat, long=long)
        location_d = GeocodingLocationDataclass(
                id=id, 
                name=name, 
                country=country,
                coordinates=coordinates,
                importance=importance,
                type=models.LocationTypeEnum.city,
                )

        ret.append(location_d)
    return ret

class GeocodingAPI(api.RapidAPIBase):
    """A class wrapper around a Forward & Reverse Geooding API from RapidAPI.

    This class implements only one method of the API which is used to get 
    a full city information from a user-written query.

    Attributes:
        base_url: a class defined string url to be used to query API from
        host: a class defined string representing host to be used in RapidAPI
        locale: a class defined string representing a locale 
        specification(IBM; ISO-639, ISO-3166) to be used in API responses.
    """

    base_url = "https://forward-reverse-geocoding.p.rapidapi.com"
    host = "forward-reverse-geocoding.p.rapidapi.com"
    locale = "en_US"

    def __init__(self, api_key: str):
        """Init a class with RapidAPI user-application API key"""
        super().__init__(api_key=api_key, api_host=self.host)


    def forward_geocoding(
            self,
            city: str,
            **kwargs,
            ) -> List[models.CityLocationDataclass]:
        """Returns a list of cities found from forward geocoding.

        Retrieves info from /v1/forward geocoding API and stores it in a list
        of dataclasses.

        Args:
            city: a string containing a city to search for

        Returns:
            A list of GeocodingLocationDataclass that represent info about
            found cities for example a repr of one element:
            GeocodingLocationDataclass(
                id=304519492, 
                name='New York', 
                type=<LocationTypeEnum.city: 'CITY'>, 
                coordinates=CoordinatesDataclass(
                    lat='40.7127281', 
                    long='-74.0060152'
                ), 
                country='United States', 
                importance=0.81757661145185
            )

        Note:
            - the returned model of GeocodingLocationDataclass should not
            be relied upon if you are building a user-space code to retrieve
            info about a city. Instead a models.CityLocationDataclass should
            be used

            - additional keyword arguments could be provided to the api call 
            using kwargs argument, but be careful to do so from the user-code
            the signature of just getting a city is pretty generic and should
            be relied upon in future implementations of any geocoding apis

        """ 

        url = "{0}/v1/forward".format(self.base_url)
        params = {
                "city": city,
                "accept-language": self.locale,
                **kwargs
                  }
        r = self._session.get(url, params=params)
        return _parse_locations_from_geocoding(r.json())
        
