from json import loads
import os


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
    def __init__(self, name, path, fields, dirpath=''):
        self.name = name
        self.path = os.path.join(dirpath, path)
        self.fields = {
            field_dict['name'].lower(): Field.fromdict(field_dict)
            for field_dict in fields
        }

    @property
    def valid(self):
        return all(f.value for f in self.fields.values())

    @property
    def missing(self):
        return [k for k, v in self.fields.items() if not v.value]

    @property
    def copy(self):
        return self.__class__(self.name, self.path, [f.copy() for f in self.fields])

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
            if os.path.isfile(v.path)]
