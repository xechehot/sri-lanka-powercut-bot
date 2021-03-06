import logging
from datetime import datetime
from typing import Dict, Tuple, List, Callable, Any

from lib.exception import UpdateExpiredValueError

logger = logging.getLogger(__name__)


class ExpiringCache(object):
    cache: Dict[Tuple[str, str], Tuple[datetime, Any]]

    def __init__(self, init_fun: Callable[[Tuple[str, str]], Any],
                 expiration_seconds: int, fallback_on_update: bool = False):
        self.cache = {}
        self.init_fun = init_fun
        self.expiration_seconds = expiration_seconds
        self.fallback_on_update = fallback_on_update

    @staticmethod
    def now():
        return datetime.now()

    def is_expired(self, created) -> bool:
        return (self.now() - created).seconds > self.expiration_seconds

    def get(self, key: Tuple[str, str]):
        value = self.cache.get(key)
        created, payload = None, None
        if value:
            created, payload = value
        if not value or self.is_expired(created):
            logger.debug('Refreshing value for %s created on %s', key, created)
            try:
                payload = self.init_fun(key)
                self.cache[key] = (self.now(), payload)
            except UpdateExpiredValueError:
                if self.fallback_on_update and value:
                    return value[1]
                else:
                    raise UpdateExpiredValueError("Updating cached value failed")
        return payload
