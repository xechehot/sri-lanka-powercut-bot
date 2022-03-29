from io import BytesIO
from typing import Tuple
import logging

import requests

from lib.exception import UpdateExpiredValueError
from lib.pdf_parser import PdfParser
from lib.schedule_cache import ExpiringCache
from os import environ

from lib.web_parser import PowerCutWebParser

logger = logging.getLogger(__name__)

DEFAULT_SCHEDULE_EXPIRATION = 60 * 30
SCHEDULE_CACHE_EXPIRATION = int(environ.get('SCHEDULE_CACHE_EXPIRATION', DEFAULT_SCHEDULE_EXPIRATION))

DEFAULT_PDF_LIST_EXPIRATION = 60 * 10
PDF_LIST_CACHE_EXPIRATION = int(environ.get('PDF_LIST_CACHE_EXPIRATION', DEFAULT_PDF_LIST_EXPIRATION))

POWER_CUT_PAGE_KEY = 'POWER_CUT_PAGE'

pdf_parser = PdfParser()
web_parser = PowerCutWebParser.create_pucsl_parser()


def parse_pdf_file(key: Tuple[str, str]):
    dt, pdf_link = key
    pdf_file = requests.get(pdf_link, verify=False).content
    payload = pdf_parser.parse_pdf(BytesIO(pdf_file))
    return payload


schedule_cache = ExpiringCache(parse_pdf_file,
                               expiration_seconds=SCHEDULE_CACHE_EXPIRATION)


def get_pdf_list(key):
    try:
        pdf_list = web_parser.load_pdf_list()
        logger.debug(pdf_list)
        return pdf_list
    except requests.exceptions.ConnectionError as ex:
        raise UpdateExpiredValueError(ex)


pdf_list_cache = ExpiringCache(get_pdf_list,
                               expiration_seconds=PDF_LIST_CACHE_EXPIRATION,
                               fallback_on_update=True)
