from formencode import validators as fev
from formencode import schema as fes


class Schema(fes.Schema):
    '''Subclass to allow/strip extra fields so we can include _csrf
    on all forms without having to put it in the explicit schema
    description
    '''
    allow_extra_fields = True
    filter_extra_fields = True


class FileUpload(fev.NotEmpty):

    def to_python(self, value, state=None):
        if isinstance(value, cgi.FieldStorage):
            return value
        else:
            return super(FileUpload, self).to_python(value, state)

    def from_python(self, value, state=None):
        return value


mapping_schema = Schema(
    header=fev.StringBool(),
    sheet=fev.Int(),
    email=fev.Int())

append_schema = Schema(
    file=FileUpload())

upload_schema = Schema(
    file=FileUpload(),
    mapping=mapping_schema)
