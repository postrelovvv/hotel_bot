"""A package containing functions and classes that provide info to be used in telegram bot.

Basically its an 'implementation' layer as well as some generic layers to be
be used externally in services.

Note:
    as long as it's an implementation layer, the end application should barely
    rely on the API the lib provides(could only be generic things) and implement
    its own adapters for the library, so that the end application could be
    easily separable and new functionality could be added more independently
    in library and vice versa
"""

