import bson
from pyramid.security import Authenticated, AllPermissionsList
from pyramid.security import Allow, Deny, DENY_ALL
import pyramid.httpexceptions as exc


class RequestUser(object):

    def __init__(self, request):
        self.request = request
        if request.user:
            self.__acl__ = [
                (Allow, Authenticated, AllPermissionsList()),
                DENY_ALL
            ]
        else:
            self.__acl__ = [DENY_ALL]


class List(object):
    __name__ = 'list'
    match_acl = [
        (Allow, Authenticated, ('read', 'write')),
        (Allow, 'group:dvapi', AllPermissionsList()),
        DENY_ALL]
    mismatch_acl = [
        (Allow, 'group:dvapi', AllPermissionsList()),
        DENY_ALL]

    def __init__(self, request):
        from dvlp.spreadsheet import model as M
        self.lst = M.List.query.get(
            _id=bson.ObjectId(request.matchdict['list_id']))
        if self.lst is None:
            raise exc.HTTPNotFound()
        if request.user and self.lst.user_id == request.user._id:
            self.__acl__ = self.match_acl
        else:
            self.__acl__ = self.mismatch_acl


