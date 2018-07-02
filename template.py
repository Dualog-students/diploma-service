from json import loads
from os import path


class Field(object):
    def __init__(self, color, x, y, w, h):
        self.color = color
        self.value = ""
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @classmethod
    def fromdict(cls, field_dict):
        return cls(
            field_dict['Color'],
            field_dict['XOffset'],
            field_dict['YOffset'],
            field_dict['Width'],
            field_dict['Height'])

    def copy(self):
        return self.__class__(self.color, self.x, self.y, self.w, self.h)


class Template(object):
    def __init__(self, template_dict, dirpath=''):
        self.name = template_dict['TemplateName']
        self.path = path.join(dirpath, template_dict['ResourcePath'])
        self.fields = {
            field_dict['Name'].lower(): Field.fromdict(field_dict)
            for field_dict
            in template_dict['Fields']
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


def import_templates(filename):
    with open(filename) as infile:
        dicts = loads(infile.read())

    directory_name = path.dirname(filename)

    return {template_dict['TemplateName'].lower(): Template(template_dict, dirpath=directory_name)
            for template_dict in dicts}


def valid_template_names():
    return [k for k, v
            in import_templates('templates/templates.json').items()
            if path.isfile(v.path)]
