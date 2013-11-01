from formencode import validators as fev
from formencode import schema as fes


class Schema(fes.Schema):
    '''Subclass to allow/strip extra fields so we can include _csrf
    on all forms without having to put it in the explicit schema
    description
    '''
    allow_extra_fields = True
    filter_extra_fields = True


class FileByNonce(fev.FancyValidator):

    def __init__(self, nonce_field='file_nonce', file_field='file', **kwargs):
        self.nonce_field = nonce_field
        self.file_field = file_field
        super(FileByNonce, self).__init__(**kwargs)

    def validate_python(self, value, state=None):
        from sfile import model as FM
        nonce = value[self.nonce_field]
        f = FM.File.m.find({'metadata.nonce': nonce}).first()
        if f is None:
            raise fev.Invalid(
                'File with nonce <%s> not found' % nonce, value, state)
        value[self.file_field] = f

mapping_schema = Schema(
    header=fev.StringBool(),
    sheet=fev.Int(),
    email=fev.Int())

list_schema = Schema(
    file_nonce=fev.String(),
    mapping=mapping_schema,
    chained_validators=[FileByNonce()])

append_schema = Schema(
    file_nonce=fev.String(),
    chained_validators=[FileByNonce()])
