from io import BytesIO
from typing import Tuple

import requests

from lib.pdf_parser import PdfParser
from lib.schedule_cache import ScheduleCache
from os import environ

DEFAULT_EXPIRATION = 60 * 30
SCHEDULE_CACHE_EXPIRATION = int(environ.get('SCHEDULE_CACHE_EXPIRATION', DEFAULT_EXPIRATION))

pdf_parser = PdfParser()


def parse_pdf_file(key: Tuple[str, str]):
    dt, pdf_link = key
    pdf_file = requests.get(pdf_link, verify=False).content
    payload = pdf_parser.parse_pdf(BytesIO(pdf_file))
    return payload


schedule_cache = ScheduleCache(parse_pdf_file,
                               expiration_seconds=SCHEDULE_CACHE_EXPIRATION)
