import logging
import urllib2

from pyramid.view import view_config
from pyramid import httpexceptions as exc
from pyramid.response import Response

from sutil import util
from sevent import model as EM
from dvlp.spreadsheet import model as M
from dvlp.spreadsheet import validators as V
import tasks as T

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
    data = V.upload_schema.to_python(request.json, request)
    f = data['file']
    mapping = data['mapping']
    lst = M.List(
        user_id=request.user._id,
        url=f.url,
        mapping=mapping,
        status='new')
    request.response.status = 201
    M.odm_session.flush(lst)
    evt = EM.event.track(
        'dvlp.spreadsheet.list-created',
        request.user._id,
        list_id=lst._id)
    T.import_list.spawn(evt._id)
    raise exc.HTTPCreated(list_id=lst._id)


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
    data = V.append_schema.to_python(request.json, request)
    request.context.lst.append(data['file'])
    return request.context.lst


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
    evt = EM.event.track(
        'dvlp.spreadsheet.list-remapped',
        request.user._id,
        list_id=request.context.lst._id)
    T.import_list.spawn(evt._id)
    return data


@view_config(
    route_name='dvlp.spreadsheet.1_0.list.subscribers',
    request_method='GET',
    permission='read')
def get_subscribers(request):
    lst = request.context.lst
    r = Response(content_type='text/csv')
    r.app_iter = lst.subscriber_iter()
    return r

