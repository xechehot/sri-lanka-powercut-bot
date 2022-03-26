import re



def extract_link_date(url, name):
    matches = re.findall('\d{2}-\d{2}-\d{4}', url)
    if matches:
        d, m, y = matches[0].split('-')
        return f'{y}-{m}-{d}'
