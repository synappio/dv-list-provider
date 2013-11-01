import sutil.main
import ming.mim

from webtest import TestApp
from sutil import test_helpers
from sfile.tests import helpers as FTH


def configure_functional_oauth_app(main, **local_settings):
    filt = sutil.main.ming_filter_factory({
        'ming.dvlp_ss.uri': 'mim://',
        'ming.sauth.uri': 'mim://',
        'ming.sevent.uri': 'mim://',
        'ming.sfile.uri': 'mim://',
        'ming.chapman.uri': 'mim://',
        })
    app = main({
        'testing': True,
        }, **local_settings)
    ming.mim.Connection.get().clear_all()
    return TestAppWithOAuth(filt(app))


def make_list(user, original_file, mapping=None):
    from dvlp.spreadsheet import model as M
    if mapping is None:
        mapping = dict(header=False, sheet=0, email=0)
    with test_helpers.flushing():
        return M.List(
            user_id=user._id,
            original_file_id=original_file._id,
            mapping=mapping)


class TestAppWithOAuth(TestApp):

    def __init__(self, *args, **kwargs):
        self._token = None
        super(TestAppWithOAuth, self).__init__(*args, **kwargs)

    def authorize(self, token):
        self._token = str(token)

    def do_request(self, req, status, expect_errors):
        if self._token is not None:
            req.headers['Authorization'] = 'bearer ' + self._token
        return super(TestAppWithOAuth, self).do_request(
            req, status, expect_errors)
