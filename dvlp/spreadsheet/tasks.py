from contextlib import closing
from urllib2 import urllib

from chapman import task
from sevent.lib import listen

from sevent import model as EM
from sfile import model as FM
from sutil import util

from dvlp.spreadsheet import model as M


@listen('dvlp.spreadsheet.list-created')
@listen('dvlp.spreadsheet.list-remapped')
@task(ignore_result=True)
@util.with_mongo
def import_list(event_id):
    ev = EM.event.m.get(_id=event_id)
    lst = M.List.query.get(_id=ev.properties.list_id)
    wfp = FM.new_file(
        None,
        filename='%s-original.csv' % lst._id,
        contentType='text/csv')
    rfp = urlopen(lst.original_url)
    with wfp, closing(rfp)
        wb = Workbook.from_sfile()
