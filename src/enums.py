"""A module consists of enums that are used in bot user space."""
import enum
import functools

class StatesEnum(enum.Enum):
    """States in which the converation with user can be."""

    LOCATION = 0
    CHECKIN = 1
    CHECKOUT = 2
    HOTELS_COUNT = 3
    PRICE_RANGE = 4
    MAX_DISTANCE_DOWNTOWN = 5
    LOAD_PHOTOS = 6

class DealsCommandTypeEnum(enum.Enum):
    """All the supported deals commans."""
    low_price = "lowprice"
    high_price = "highprice"
    best_deal = "bestdeal"


    @classmethod
    def as_commands_list(cls):
        """Returns a list of commands in a way to register them as commands."""
        return [entity.value for entity in cls]

class HotelsSorterFunctionsEnum(enum.Enum):
    """Sorting functions enumeration."""

    high_price_sorted = functools.partial(
            sorted, 
            key=lambda prop: prop.price.price, 
            reverse=True
            )

    low_price_sorted = functools.partial(
            sorted, 
            key=lambda prop: prop.price.price
            )

    best_deal_sorted = functools.partial(
            sorted, 
            key=lambda prop: prop.price.price and prop.distance_from_downtown.distance
            )

    @classmethod
    def from_deals_command_type(cls, command_type: DealsCommandTypeEnum):
        """Returns a sorting function based on a command type."""
        return getattr(cls, "{0}_sorted".format(command_type.name))


