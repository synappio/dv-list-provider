import csv
import logging
import operator
import urllib2
from itertools import chain
from cStringIO import StringIO
from datetime import datetime

from pyramid.decorator import reify

from ming import Session
from ming import schema as S
from ming import collection, Field
from ming.orm import ThreadLocalODMSession

from sutil import util
from lib import Workbook

log = logging.getLogger(__name__)

doc_session = Session.by_name('dvlp_ss')
odm_session = ThreadLocalODMSession(doc_session)

list_ = collection(
    'list', doc_session,
    Field('_id', S.ObjectId()),
    Field('created', datetime, if_missing=datetime.utcnow),
    Field('status', str, if_missing='active'),
    Field('user_id', S.ObjectId, if_missing=None, index=True),
    Field('url', str),
    Field('mapping', dict(
        header=bool,
        sheet=int,
        email=int)),
    Field('stats', {str: None}))


class List(object):

    def __json__(self, request=None):
        return dict(
            id=str(self._id),
            mapping=self.mapping,
            stats=self.stats)

    def subscriber_iter(self):
        with closing(urllib2.urlopen(self.url)) as socket:
            wb = Workbook.from_file(socket)
        rdr = enumerate(wb.sheet_iter(self.mapping.sheet))
        if self.mapping.header:
            rdr.next()
        else:
            rdr = ((rownum + 1, row) for (rownum, row) in rdr)
        for rows in util.chunk(rdr, 100):
            fp = StringIO()
            wr = csv.writer(fp)
            for rownum, row in rows:
                wr.writerow([rownum, row[self.mapping.email]])
            yield fp.getvalue()

    def append(self, f):
        with closing(urllib2.urlopen(self.url)) as socket:
            wb = Workbook.from_file(socket)
        rdr0 = enumerate(wb.sheet_iter(self.mapping.sheet))
        if not self.mapping.header:
            rdr0 = chain(
                [(0, None)],
                ((rownum + 1, row) for (rownum, row) in rdr0))
        rfp = FM.File.m.get_file(f._id)
        wfp = FM.File.m.new_file(
            f.filename + '-appended.csv',
            contentType='text/csv')
        self.appended_file_id = wfp._id
        with rfp, wfp:
            rdr1 = csv.reader(util.Linereader(rfp))
            wr = csv.writer(wfp)
            key0 = operator.itemgetter(0)
            key1 = lambda row: int(row[0])
            for val0, val1 in util.right_join(rdr0, rdr1, key0, key1):
                if val0 is None:
                    row0 = []
                else:
                    row0 = val0[1]
                if val1 is None:
                    row1 = []
                else:
                    row1 = val1
                if row0 is None:
                    row0 = []
                if row1 is None:
                    row1 = []
                wr.writerow(row1 + row0)

odm_session.mapper(List, list_, properties=dict())
