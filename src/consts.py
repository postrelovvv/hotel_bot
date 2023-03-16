"""A module that consists of all the constants that are used accross the bot space."""
import re

DATE_FORMAT = "%d.%m.%Y"
PRICE_RANGE_FORMAT_RE = re.compile(r"^\d{1,}-\d{1,10}$")
PRICE_RANGE_SEPARATOR = "-"
BOOL_ANSWER = {"да": True, "нет": False}

