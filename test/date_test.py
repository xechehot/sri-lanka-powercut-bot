from lib.date import extract_link_date


def test_extract_link_date():
    url = 'https://www.pucsl.gov.lk/wp-content/uploads/2022/03/E-25-03-2022-Power-Interruption-Schedule-full.pdf'
    name = 'Power Interruption Schedule 25-March-2022- Friday'
    assert extract_link_date(url, name) == '2022-03-25'


def test_extract_empty_link_date():
    assert extract_link_date('https://some-link-without-date-2020/03', 'some name') is None
