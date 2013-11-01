import logging
from datetime import datetime

from pyramid.decorator import reify

from ming import Session
from ming import schema as S
from ming import collection, Field
from ming.orm import ThreadLocalODMSession

from sfile import model as FM

log = logging.getLogger(__name__)

doc_session = Session.by_name('dvlp_ss')
odm_session = ThreadLocalODMSession(doc_session)

list_ = collection(
    'list', doc_session,
    Field('_id', S.ObjectId()),
    Field('created', datetime, if_missing=datetime.utcnow),
    Field('status', str, if_missing='active'),
    Field('user_id', S.ObjectId, if_missing=None, index=True),
    Field('original_file_id', S.ObjectId, if_missing=None),
    Field('appended_file_id', S.ObjectId, if_missing=None),
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

    @reify
    def original_file(self):
        return FM.File.m.get_file(self.original_file_id)

odm_session.mapper(List, list_, properties=dict())
