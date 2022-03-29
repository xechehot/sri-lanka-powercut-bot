from typing import Dict

import requests
from bs4 import BeautifulSoup

from lib.date import extract_link_date

POWER_CUT_URL = 'https://www.pucsl.gov.lk/power-interruption-schedule-25-feb-2022/'


class PowerCutWebParser(object):
    def __init__(self, url):
        self.url = url

    @classmethod
    def create_pucsl_parser(cls):
        return cls(POWER_CUT_URL)

    def _get_page(self):
        return requests.get(self.url, verify=False, timeout=10).text

    @staticmethod
    def _map_pdfs(hrefs) -> Dict[str, str]:
        res = {}
        for url, name in hrefs:
            extracted_date = extract_link_date(url, name)
            if extracted_date:
                res[extracted_date] = url
        return dict(sorted(res.items(), reverse=True))

    def load_pdf_list(self):
        page = self._get_page()
        soup = BeautifulSoup(page, "html.parser")
        news_box = soup.find('div', class_='in-news-box')
        hrefs = news_box.find_all('a')
        link_pairs = ((link.attrs['href'], link.contents[0]) for link in hrefs)
        return self._map_pdfs(link_pairs)
