import requests
from bs4 import BeautifulSoup

from lib.date import extract_link_date

POWER_CUT_URL = 'https://www.pucsl.gov.lk/power-interruption-schedule-25-feb-2022/'


class PowerCutWebParser(object):
    def __init__(self, url):
        self.url = url

    @staticmethod
    def create_pucsl_parser(self):
        return self.__init__(POWER_CUT_URL)

    def _get_page(self):
        return requests.get(self.url, verify=False).text

    @staticmethod
    def _map_pdfs(hrefs):
        res = {}
        for url, name in hrefs:
            extracted_date = extract_link_date(url, name)
            if extracted_date:
                res[extracted_date] = url
        return res

    def load_pdf_list(self):
        page = self._get_page()
        soup = BeautifulSoup(page, "html.parser")
        news_box = soup.find('div', class_='in-news-box')
        hrefs = news_box.find_all('a')
        link_pairs = ((link.attrs['href'], link.contents[0]) for link in hrefs)
        return self._map_pdfs(link_pairs)
