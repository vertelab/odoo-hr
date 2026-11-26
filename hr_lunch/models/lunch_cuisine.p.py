"""OSM `cuisine` tags mapped to lunch tags.

OSM writes `cuisine` as a free-text, semicolon-separated list in English
(`italian;greek`). The catalogue's tags are Swedish. The mapping between them
is a table, not a guess: an unknown value gets no tag and a warning, so a new
OSM value shows up in the log instead of silently becoming "Other".
"""

import logging

_logger = logging.getLogger(__name__)

# OSM cuisine value -> lunch.tag name. `regional` maps to None on purpose: it
# means "the local kitchen", and turning that into a Swedish tag would be an
# interpretation of the restaurant, not a translation of the value.
CUISINE_MAP = {
    "italian": "Italienskt",
    "greek": "Grekiskt",
    "sushi": "Sushi",
    "pizza": "Pizza",
    "burger": "Burgare",
    "kebab": "Kebab",
    "thai": "Thailändskt",
    "indian": "Indiskt",
    "chinese": "Kinesiskt",
    "vietnamese": "Vietnamesiskt",
    "japanese": "Japanskt",
    "mexican": "Mexikanskt",
    "salad": "Sallad",
    "mediterranean": "Medelhavsmat",
    "american": "Amerikanskt",
    "barbecue": "BBQ",
    "regional": None,
}


def map_cuisine(cuisine_string):
    """Tag names for an OSM `cuisine` value, in the order given.

    Splits on ';', trims, lowercases and looks each value up. Unknown values
    and values mapped to None are logged and skipped — no tag, no fallback.
    Duplicates are dropped so `pizza;pizza` gives one tag.
    """
    if not cuisine_string:
        return []

    tags = []
    for raw_value in cuisine_string.split(";"):
        value = raw_value.strip().lower()
        if not value:
            continue
        if value not in CUISINE_MAP:
            _logger.warning(
                "Unmapped cuisine value %r in %r — no tag set", value, cuisine_string
            )
            continue
        tag_name = CUISINE_MAP[value]
        if tag_name is None:
            _logger.warning(
                "Cuisine value %r is an interpretation, not a translation — "
                "no tag set for %r", value, cuisine_string
            )
            continue
        if tag_name not in tags:
            tags.append(tag_name)
    return tags


def apply_cuisine_tags(restaurant, cuisine_string):
    """Create/find the cuisine tags and put them on the restaurant.

    Returns the tags that were set. An unknown cuisine leaves the restaurant
    untouched: the caller has already created it from an explicit choice, and
    a missing tag is not a reason to fail.
    """
    tag_names = map_cuisine(cuisine_string)
    if not tag_names:
        return restaurant.env["lunch.tag"]

    Tag = restaurant.env["lunch.tag"]
    tags = Tag
    for name in tag_names:
        tag = Tag.search([("name", "=", name)], limit=1)
        if not tag:
            tag = Tag.create({"name": name, "tag_type": "cuisine"})
        tags |= tag
    restaurant.write({"tag_ids": [(4, tag.id) for tag in tags]})
    return tags
