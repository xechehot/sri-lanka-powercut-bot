import time

from lib.schedule_cache import ScheduleCache


def test_value_cached():
    execution_list = []
    expected_payload = ['A'], ['08:30 - 11:00']

    def execute(key):
        execution_list.append(0)
        return expected_payload

    schedule_cache = ScheduleCache(execute, 100)
    assert len(execution_list) == 0
    actual_payload = schedule_cache.get('KEY')
    assert actual_payload is not None
    assert actual_payload == expected_payload
    assert len(execution_list) == 1
    actual_payload = schedule_cache.get('KEY')
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

    schedule_cache = ScheduleCache(execute, 1)

    assert len(execution_list) == 0
    actual_payload = schedule_cache.get('KEY')
    assert actual_payload is not None
    assert actual_payload == invalidated_payload
    assert len(execution_list) == 1
    actual_payload = schedule_cache.get('KEY')
    assert actual_payload is not None
    assert actual_payload == invalidated_payload
    assert len(execution_list) == 1
    time.sleep(2)
    actual_payload = schedule_cache.get('KEY')
    assert actual_payload is not None
    assert actual_payload == new_payload
    assert len(execution_list) == 2
