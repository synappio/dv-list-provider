import logging
from itertools import islice

import xlrd

log = logging.getLogger(__name__)


class Workbook(object):
    EXCEL_TYPES = [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]

    def __init__(self, f):
        self.f = f
        self.sheets = []

    def __json__(self, request=None):
        return dict(
            sheets=[s.__json__(request) for s in self.sheets])

    @classmethod
    def from_sfile(cls, f, limit_rows=None):
        if f.contentType in cls.EXCEL_TYPES:
            try:
                self = ExcelWorkbook(f)
                self.refresh(limit_rows)
                return self
            except Exception as err:
                log.error('Error in %s with %s: %r', type_, f._id, err)
        return None


class ExcelWorkbook(Workbook):

    def refresh(self, limit_rows=None):
        with M.File.m.get_file(self.f._id) as fp:
            self.wb = xlrd.open_workbook(
                self.f.filename, file_contents=fp.read())
        self.sheets = []
        for i, xl_sheet in enumerate(self.wb.sheets()):
            sheet = Sheet(xl_sheet.name)
            self.sheets.append(sheet)
            rdr = self.sheet_iter(i)
            if limit_rows:
                rdr = islice(rdr, limit_rows)
            sheet.rows = list(rdr)

    def sheet_iter(self, sheet_num):
        xl_sheet = self.wb.sheet_by_index(sheet_num)
        rownum_iter = xrange(xl_sheet.nrows)
        for rownum in rownum_iter:
            row = xl_sheet.row_values(rownum)
            row = [unicode(cell).encode('utf-8') for cell in row]
            yield row


class Sheet(object):

    def __init__(self, name):
        self.name = name
        self.rows = []

    def __json__(self, request=None):
        return dict(
            name=self.name,
            rows=[dict(row=row) for row in self.rows])
