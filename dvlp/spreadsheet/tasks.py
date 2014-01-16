from contextlib import closing
from urllib2 import urllib

from chapman import task
from sevent.lib import listen
import libcloud.security
from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver

from sevent import model as EM
from sfile import model as FM
from sutil import util

from dvlp.spreadsheet import model as M
from lib import Workbook

libcloud.security.VERIFY_SSL_CERT = False

@listen('dvlp.spreadsheet.list-created')
@listen('dvlp.spreadsheet.list-remapped')
@task(ignore_result=True)
@util.with_mongo
def import_list(event_id):
    Driver = get_driver('S3_AP_NORTHEAST')
    driver = Driver('AKIAIZ7UL3KZY2QQVXUA','Yz3JzSR4rjFgTtNhcx6GpKR2Y6qBc9jFuOv')
    container = driver.get_container('dv-dev')

    ev = EM.event.m.get(_id=event_id)
    lst = M.List.query.get(_id=ev.properties.list_id)

    with FM.File.m.find(_id=lst.original_file_id) as fp:
        obj_name = fp.filename
        obj = container.upload_object_via_stream(iterator=fp,object_name=obj_name)
        lst.status = 'new'
