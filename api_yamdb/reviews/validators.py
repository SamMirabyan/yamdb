import datetime as dt

from django.core.exceptions import ValidationError


def year_validator(value):
    year = dt.datetime.now().year
    if value < 0 or value > year:
        raise ValidationError('В обсуждении участвуют произведения нашей эры')
    return value
