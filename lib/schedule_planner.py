from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class SchedulePlanner(object):
    tz_info = ZoneInfo('Asia/Colombo')
    dt_format = '%Y-%m-%d'

    def now(self) -> datetime:
        return datetime.now(tz=self.tz_info)

    @property
    def today(self) -> str:
        return self.now().strftime(self.dt_format)

    @property
    def tomorrow(self) -> str:
        dt = self.now() + timedelta(days=1)
        return dt.strftime(self.dt_format)