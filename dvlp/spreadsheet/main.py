import logging

from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from paste.deploy.converters import asbool

from sutil import util

log = None
R = None


def main(global_config, **local_settings):
    global log, R
    from dvlp.spreadsheet import resources as R  # noqa
    import sauth.lib
    from sauth.lib import OauthAuthenticationPolicy
    from sauth.lib import RequestWithUserAttribute

    log = logging.getLogger(__name__)

    settings = dict(global_config)
    settings.update(local_settings)
    util.update_settings_from_environ(settings)
    if asbool(settings.get('testing', 'false')):
        sauth.lib.CRYPTO_TIME = 0.001
    config = Configurator(
        settings=settings,
        authentication_policy=OauthAuthenticationPolicy(),
        authorization_policy=ACLAuthorizationPolicy(),
        request_factory=RequestWithUserAttribute)
    config.add_renderer(None, 'pyramid.renderers.json_renderer_factory')
    config.include(_api_1_0, route_prefix='/1.0')
    app = config.make_wsgi_app()
    return app


def _api_1_0(config):
    config.add_route(
        'dvlp.spreadsheet.1_0', '/', factory=R.RequestUser)
    config.add_route(
        'dvlp.spreadsheet.1_0.lists', '/list/', factory=R.RequestUser)
    config.add_route(
        'dvlp.spreadsheet.1_0.list', '/list/{list_id}/', factory=R.List)
    config.add_route(
        'dvlp.spreadsheet.1_0.list.mapping',
        '/list/{list_id}/mapping/',
        factory=R.List)
    config.add_route(
        'dvlp.spreadsheet.1_0.list.subscribers',
        '/list/{list_id}/subscribers/',
        factory=R.List)
    config.scan('dvlp.spreadsheet.views')
    config.scan('sutil.error_views')
