import re
from typing import BinaryIO

from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams
from io import BytesIO, StringIO

from lib.exception import PdfParseError


class PdfParser(object):

    def __init__(self):
        pass

    def _convert_pdf_to_txt(self, stream: BytesIO):
        res_mgr = PDFResourceManager()
        ret_data = StringIO()
        txt_converter = TextConverter(res_mgr, ret_data, laparams=LAParams())
        interpreter = PDFPageInterpreter(res_mgr, txt_converter)
        for page in PDFPage.get_pages(stream):
            interpreter.process_page(page)
        return ret_data.getvalue()

    @staticmethod
    def is_table_name(x):
        return x == 'Table 01' or x == 'Table 02'

    @staticmethod
    def is_match(pattern, x):
        matches = re.match(pattern, x)
        if matches:
            return matches[0]

    def is_period(self, x):
        return self.is_match('\d\d:\d\d\s*[–\–-]?\s*\d\d[:;]\d\d', x)

    def is_group(self, x):
        return self.is_match('([A-Z]\s*,?\s*)+$', x)

    def get_schedule(self, groups, periods, group_name):
        res = []
        for g, p in zip(groups, periods):
            if group_name in g:
                res.append(p)
        return res

    def parse_pdf(self, stream: BinaryIO):
        txt = self._convert_pdf_to_txt(stream)
        periods = []
        groups = []
        table_counts = 0
        for line in txt.split('\n'):
            sline = line.strip()
            #     print(line)
            period = self.is_period(sline)
            if period:
                periods.append(period)
                continue
            group = self.is_group(sline)
            if group:
                groups.append(group)
                continue
            is_table = self.is_table_name(sline)
            if is_table:
                table_counts += 1
                if table_counts == 2:
                    break
        if len(groups) != len(periods):
            raise PdfParseError(f'Groups count {len(groups)} is not equal periods count {len(periods)}')
        return groups, periods

        # assert len(groups) == len(periods), 'groups count %d is not equal periods count %d' % (
        #     len(groups), len(periods))

# pdf_file = requests.get(link.attrs['href'], verify=False)
# i_f = BytesIO(pdf_file.content)

# print(txt)
# with open(output,'w') as of:
#     of.write(txt)