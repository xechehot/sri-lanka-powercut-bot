import logging
from datetime import datetime
from typing import Dict, Tuple, List, Callable

logger = logging.getLogger(__name__)


class ScheduleCache(object):
    cache: Dict[Tuple[str, str], Tuple[datetime, Tuple[List, List]]]

    def __init__(self, init_fun: Callable[[Tuple[str, str]], Tuple[List, List]],
                 expiration_seconds: int):
        self.cache = {}
        self.init_fun = init_fun
        self.expiration_seconds = expiration_seconds

    @staticmethod
    def now():
        return datetime.now()

    def is_expired(self, created):
        return (self.now() - created).seconds > self.expiration_seconds

    def get(self, key: Tuple[str, str]):
        value = self.cache.get(key)
        created, payload = None, None
        if value:
            created, payload = value
        if not value or self.is_expired(created):
            logger.debug('Refreshing value for %s created on %s', key, created)
            payload = self.init_fun(key)
            self.cache[key] = (self.now(), payload)
        return payload