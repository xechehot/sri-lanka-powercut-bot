from io import BytesIO

from lib.pdf_parser import PdfParser
from lib.schedule_planner import SchedulePlanner


def test_is_period():
    pdf_parser = PdfParser()
    assert pdf_parser.is_period('08:00 - 11:20') == '08:00 - 11:20'


def test_is_group():
    pdf_parser = PdfParser()
    assert pdf_parser.is_group('A, B,C') == 'A, B,C'


def test_parse_groups_periods():
    pdf_parser = PdfParser()
    with open('content/power_cut_schedule.pdf', 'rb') as f:
        res = pdf_parser.parse_pdf(f)
    assert res is not None
    groups, periods = res
    assert len(groups) == 14
    assert len(periods) == 14

    expected_periods = ['15:30 - 16:30', '19:50 -21:30']
    assert SchedulePlanner().get_schedule(groups, periods, 'W') == expected_periods


def test_parse_bad_pdf():
    pdf_parser = PdfParser()
    with open('content/E-01-03-2022-wrong.pdf', 'rb') as f:
        res = pdf_parser.parse_pdf(f)
    assert res is not None
    groups, periods = res
    assert len(groups) == 6
    assert len(periods) == 6

    expected_periods = ['8:30-11:30', '11:30-14:30', '14:30-17:30', '8:30-11:30', '11:30-14:30', '14:30-17:30']
    assert periods == expected_periods
    expected_groups = ['A', 'B', 'C', 'P,Q,R', 'S, T', 'U,V,W']
    assert groups == expected_groups
    assert SchedulePlanner().get_schedule(groups, periods, 'Q') == ['8:30-11:30']


def test_parse_bad_pdf2():
    pdf_parser = PdfParser()
    with open('content/E-04-04-2022.pdf', 'rb') as f:
        res = pdf_parser.parse_pdf(f)
    assert res is not None
    groups, periods = res
    print(periods)
    print(groups)
    assert len(groups) == 9
    assert len(periods) == 9

    expected_periods = ['10.00-13.30', '13.30-17.00', '18.00-19.30', '19.30-21.00', '10.00-13.30', '13.30-17.00', '18.00-19.30', '19.30-21.00', '06:00-10:00']

    assert periods == expected_periods
    expected_groups = ['A, B, C, D, E, F', 'G, H, I, J, K, L', 'A, B, C, D, E, F', 'G, H, I, J, K, L', 'P,Q,R,S', 'T,U,V,W', 'P,Q,R,S', 'T,U,V,W', 'CC1']
    assert groups == expected_groups
    assert SchedulePlanner().get_schedule(groups, periods, 'Q') == ['10.00-13.30', '18.00-19.30']


if __name__ == '__main__':
    test_parse_bad_pdf2()
