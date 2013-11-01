import csv
import logging
from cStringIO import StringIO


from pyramid.view import view_config
from pyramid import httpexceptions as exc
from pyramid.response import Response

import sfile.lib
from sevent import model as EM
from sutil import util

from dvlp.spreadsheet import model as M
from dvlp.spreadsheet import validators as V

log = logging.getLogger(__name__)


@view_config(
    route_name='dvlp.spreadsheet.1_0',
    request_method='GET',
    permission='read')
def root(request):
    r = dict(version='1.0', user=None)
    if request.user:
        r['user'] = request.user.name
    return r


@view_config(
    route_name='dvlp.spreadsheet.1_0.lists',
    request_method='GET',
    permission='read')
def get_lists(request):
    spec = dict(
        user_id=request.user._id,
        status='active')
    return dict(
        lists=M.List.query.find(spec).all())


@view_config(
    route_name='dvlp.spreadsheet.1_0.lists',
    request_method='POST',
    permission='write')
def create_list(request):
    data = V.list_schema.to_python(request.json, request)
    lst = M.List(
        original_file_id=data['file']._id,
        mapping=data['mapping'])
    request.response.status = 201
    M.odm_session.flush(lst)
    EM.event.track(
        'dvlp.spreadsheet.list-created',
        request.user._id,
        list_id=lst._id)
    return lst


@view_config(
    route_name='dvlp.spreadsheet.1_0.list',
    request_method='GET',
    permission='read')
def get_list(request):
    return request.context.lst


@view_config(
    route_name='dvlp.spreadsheet.1_0.list',
    request_method='POST',
    permission='write')
def append_list(request):
    '''This is what Synapp.io actually does to the list'''
    raise NotImplementedError('append_list')
    return {}


@view_config(
    route_name='dvlp.spreadsheet.1_0.list',
    request_method='DELETE',
    permission='write')
def delete_list(request):
    request.context.lst.status = 'inactive'
    raise exc.HTTPNoContent()


@view_config(
    route_name='dvlp.spreadsheet.1_0.list.mapping',
    request_method='PUT',
    permission='write')
def remap_list(request):
    data = V.mapping_schema.to_python(request.json, request)
    request.context.lst.mapping = data
    M.odm_session.flush(request.context.lst)
    EM.event.track(
        'dvlp.spreadsheet.list-remapped',
        request.user._id,
        list_id=request.context.lst._id)
    return data


@view_config(
    route_name='dvlp.spreadsheet.1_0.list.subscribers',
    request_method='GET',
    permission='read')
def get_subscribers(request):
    lst = request.context.lst
    wb = sfile.lib.Workbook.from_sfile(lst.original_file)
    rdr = enumerate(wb.sheet_iter(lst.mapping.sheet))
    if lst.mapping.header:
        rdr.next()
    r = Response(content_type='text/csv')
    def app_iter():
        for rows in util.chunk(rdr, 100):
            fp = StringIO()
            wr = csv.writer(fp)
            for rownum, row in rows:
                wr.writerow([rownum, row[lst.mapping.email]])
            yield fp.getvalue()
    r.app_iter = app_iter()
    return r


