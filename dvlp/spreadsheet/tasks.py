import urllib2
from contextlib import closing

from chapman import task
from sevent.lib import listen
from sutil import util
from sevent import model as EM
from dvlp.spreadsheet import model as M
from lib import Workbook


@listen('dvlp.spreadsheet.list-created')
@listen('dvlp.spreadsheet.list-remapped')
@task(ignore_result=True)
@util.with_mongo
def import_list(event_id):

    ev = EM.event.m.get(_id=event_id)
    lst = M.List.query.get(_id=ev.properties.list_id)

    # read file associated with list and get spreadsheet contents

    with closing(urllib2.urlopen(lst.url)) as socket:
        wb = Workbook.from_file(socket)
