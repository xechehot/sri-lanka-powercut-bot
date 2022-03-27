import re
from datetime import datetime


def extract_link_date(url, name):
    matches = re.findall('\d{2}-\d{2}-\d{4}', url)
    if matches:
        d, m, y = matches[0].split('-')
        return f'{y}-{m}-{d}'
    else:
        date_matches = re.findall('\d{2}-[a-zA-Z]+-20\d{2}', name)
        if date_matches:
            try:
                dt = datetime.strptime(date_matches[0], '%d-%B-%Y')
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                return None
