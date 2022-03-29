from datetime import datetime, timedelta
from io import StringIO
from os import linesep
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

    @staticmethod
    def get_schedule(groups, periods, group_name):
        res = []
        for g, p in zip(groups, periods):
            if group_name in g:
                res.append(p)
        return res

    @staticmethod
    def get_schedule_message(schedule, pdf_link, dt, group_name):
        message = StringIO()
        message.write(f'[Powercut schedule]({pdf_link}) for {dt} in {group_name}:')
        message.write(linesep)
        message.write(linesep)
        for s in schedule:
            message.write('🕯')
            message.write(s)
            message.write(linesep)
        return message.getvalue()
