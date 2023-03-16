"""
This module contains of either ABC classes for the library or Base classes.

By the moment of writin this comment it has next base classes:
    RapidAPIBase


Usage:
    Well, basically derive from the objects listed here like this:
    class MyGreatAPI(RapidAPIBase)

"""
import requests

class RapidAPIBase:
    """Base class for interacting with RapidAPIBase.

    This class defines initial requirements needed for interacting with a
    variety of RapidApi apis.
    It uses requests library as a Session creator and so derived class
    should rely on the requests' library api provided by its Session class.
    The session is held dynamically in ._session attribute of the class instance.

    Attributes:
        _api_key: a string containing key to be used with rapidapi
        _api_host: a string containing host of the api to interact with
        _session: a Session object from requests library that is being used as
            requests governor

    Note:
        The api key in rapid api is shared across all the apis it provides,
        but api host is kind of 'unique' to each of the api you would like to
        interact with.

    """


    def __init__(self, api_key: str, api_host: str):
        """Init class with api key and api host to be used with rapid api."""

        self._api_key = api_key
        self._api_host = api_host


        self._session = requests.Session()
        headers = {
                "X-RapidAPI-Key": self._api_key,
                "X-RapidAPI-Host": self._api_host
                }

        self._session.headers.update(headers)
