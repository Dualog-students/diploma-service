from json import loads
import os


class BadSignature(ValueError):
    pass


class Field(object):
    def __init__(self, name, color, x, y, w, h):
        self.color = color
        self.value = ""
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @classmethod
    def fromdict(cls, field_dict):
        return cls(**field_dict)

    def copy(self):
        return self.__class__(None, self.color, self.x, self.y, self.w, self.h)


class Template(object):
    def __init__(self, name, path, fields, signature=None, dirpath=''):
        self.name = name
        self.path = os.path.join(dirpath, path)
        self.fields = {
            field_dict['name'].lower(): Field.fromdict(field_dict)
            for field_dict in fields
        }
        self._signature = Field.fromdict(signature) if signature else None

    @property
    def signature(self):
        if self._signature:
            return self._signature
        else:
            return None

    @signature.setter
    def signature(self, value):
        if not value.endswith('.png'):
            value += ".png"
        if value and not os.path.exists(value):
            new_value = 'signatures/' + value
            if not os.path.exists(new_value):
                raise BadSignature(f"{value} is not a valid signature")
            else:
                value = new_value
        self._signature.value = value

    @property
    def valid(self):
        file_exists = os.path.exists(self.path)
        if self.signature and self.signature.value:
            signature_exists = os.path.exists(self.signature.value)
        else:
            signature_exists = True
        fields_valid = all(f.value for f in self.fields.values())
        return file_exists and signature_exists and fields_valid

    @property
    def empty_fields(self):
        return [k for k, v in self.fields.items() if not v.value]

    @property
    def copy(self):
        signature = self.signature.copy if self.signature else None
        return self.__class__(self.name, self.path, [f.copy() for f in self.fields], signature)

    @classmethod
    def from_dict(cls, template_dict, dirpath=''):
        template_dict['dirpath'] = dirpath
        return cls(**template_dict)


def import_templates(filename):
    with open(filename) as infile:
        dicts = loads(infile.read())

    directory_name = os.path.dirname(filename)

    return {template_dict['name'].lower(): Template.from_dict(template_dict, dirpath=directory_name)
            for template_dict in dicts}


def valid_template_names():
    return [k for k, v
            in import_templates('templates/templates.json').items()
            if os.path.exists(v.path)]
