from lib.web_parser import PowerCutWebParser


def test_load_pdf_list(monkeypatch):
    web_parser = PowerCutWebParser.create_pucsl_parser()

    def get_mock_page():
        with open('content/power_cut.html', 'r') as f:
            return f.read()

    # Application of the monkeypatch to replace Path.home
    # with the behavior of mockreturn defined above.
    monkeypatch.setattr(web_parser, "_get_page", get_mock_page)

    assert web_parser._get_page()[:10] == '<!DOCTYPE '
    actual_pdf_map = web_parser.load_pdf_list()
    assert len(actual_pdf_map) == 33
    assert '2022-03-23' in actual_pdf_map

    expected_url = 'https://www.pucsl.gov.lk/wp-content/uploads/2022/03/E-23-03-2022-Power-Interruption-Schedule-full.pdf'
    assert actual_pdf_map['2022-03-23'] == expected_url

    d, link = next(iter(actual_pdf_map.items()))
    assert d == '2022-03-27'


