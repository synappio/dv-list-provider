import logging


from pyramid.view import view_config
from pyramid import httpexceptions as exc
from pyramid.response import Response

from sevent import model as EM
from sfile import model as FM

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
    r = Response(content_type='text/csv')
    r.app_iter = lst.subscriber_iter()
    return r


@view_config(
    route_name='dvlp.spreadsheet.1_0.list.appended',
    request_method='GET',
    permission='read')
def get_appended(request):
    lst = request.context.lst
    return FM.file_response(lst.appended_file)
