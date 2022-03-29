import time

import pytest

from lib.exception import UpdateExpiredValueError
from lib.schedule_cache import ExpiringCache

KEY = 'key', 'link'


def test_value_cached():
    execution_list = []
    expected_payload = ['A'], ['08:30 - 11:00']

    def execute(key):
        execution_list.append(0)
        return expected_payload

    schedule_cache = ExpiringCache(execute, 100)
    assert len(execution_list) == 0
    actual_payload = schedule_cache.get(KEY)
    assert actual_payload is not None
    assert actual_payload == expected_payload
    assert len(execution_list) == 1
    actual_payload = schedule_cache.get(KEY)
    assert actual_payload is not None
    assert actual_payload == expected_payload
    assert len(execution_list) == 1


def test_invalidate_cached_value():
    execution_list = []
    invalidated_payload = ['A'], ['08:30 - 11:00']
    new_payload = ['B'], ['20:00 - 23:00']
    payload_list = [invalidated_payload, new_payload]

    def execute(key):
        payload = payload_list[len(execution_list)]
        execution_list.append(0)
        return payload

    schedule_cache = ExpiringCache(execute, 1)

    assert len(execution_list) == 0
    actual_payload = schedule_cache.get(KEY)
    assert actual_payload is not None
    assert actual_payload == invalidated_payload
    assert len(execution_list) == 1
    actual_payload = schedule_cache.get(KEY)
    assert actual_payload is not None
    assert actual_payload == invalidated_payload
    assert len(execution_list) == 1
    time.sleep(2)
    actual_payload = schedule_cache.get(KEY)
    assert actual_payload is not None
    assert actual_payload == new_payload
    assert len(execution_list) == 2


def test_raise_error_if_update_value_failed_without_fallback():
    def execute(key):
        raise UpdateExpiredValueError()

    schedule_cache = ExpiringCache(execute, 100)
    with pytest.raises(UpdateExpiredValueError):
        schedule_cache.get(('x', 'y'))


def test_raise_error_if_update_value_failed_with_empty_cache_with_fallback():
    def execute(key):
        raise UpdateExpiredValueError()

    schedule_cache = ExpiringCache(execute, 100, fallback_on_update=True)
    with pytest.raises(UpdateExpiredValueError):
        schedule_cache.get(('x', 'y'))


def test_return_old_value_if_update_value_failed_with_fallback():
    execution_list = []
    expected_payload = ['A'], ['08:30 - 11:00']

    def execute(key):
        if len(execution_list) == 0:
            execution_list.append(0)
            return expected_payload
        else:
            raise UpdateExpiredValueError()

    schedule_cache = ExpiringCache(execute, 1, fallback_on_update=True)

    assert len(execution_list) == 0
    actual_payload = schedule_cache.get(KEY)
    assert actual_payload is not None
    assert actual_payload == expected_payload
    assert len(execution_list) == 1
    time.sleep(1.5)
    actual_payload = schedule_cache.get(KEY)
    assert actual_payload is not None
    assert actual_payload == expected_payload
    assert len(execution_list) == 1
    time.sleep(1.5)

    schedule_cache.fallback_on_update = False
    with pytest.raises(UpdateExpiredValueError):
        schedule_cache.get(KEY)


