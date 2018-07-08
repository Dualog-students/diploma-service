from json import loads, dumps
import os

TEMPLATE_FOLDER = 'templates'
TEMPLATE_FILE = 'templates.json'
SIGNATURE_FOLDER = 'signatures'
SIGNATURE_FILE = 'signatures.json'


class BadSignature(ValueError):
    pass


class Field(object):
    def __init__(self, color, x, y, w, h):
        self.color = color
        self.value = ""
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def copy(self):
        return self.__class__(None, self.color, self.x, self.y, self.w, self.h)


class Template(object):
    def __init__(self, path, fields, signature=None):
        self.path = path
        self.fields = create_fields(fields)
        # This private instance variable will only have its
        # 'value' attribute modified by the setter for signature
        self._signature = Field(**signature) if signature else None

    @property
    def signature(self):
        if self._signature:
            return self._signature
        else:
            return None

    @signature.setter
    def signature(self, value):
        path = os.path.join(SIGNATURE_FOLDER, f"{value}.png")
        if not os.path.isfile(path):
            raise BadSignature(f"{value} is not a valid signature")
        self._signature.value = path

    @property
    def valid(self):
        file_exists = os.path.exists(self.path)
        if self.signature and self.signature.value:
            # Check if signature is set to a valid signature file
            signature_exists = os.path.exists(self.signature.value)
        else:
            # A blank signature is also fine
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


def load_json_from(filename):
    """Returns the dumped JSON metadata from filename"""
    with open(filename) as infile:
        dicts = loads(infile.read())

    return dicts


def discard_nonexistant_templates(template_dicts):
    """Returns a new dictionary of template attributes, discarding
    all templates that are not actually available on disk"""
    return {
        k: v for k, v
        in template_dicts.items()
        if os.path.isfile(os.path.join(TEMPLATE_FOLDER, v['path']))
    }


def discard_nonexistant_signatures(signature_dicts):
    """Returns a new dictionary of signature attributes, discarding
    all signatures that are not actually available on disk"""
    return [
        d for d in signature_dicts
        if os.path.isfile(os.path.join(SIGNATURE_FOLDER, d['id'] + '.png'))
    ]


def create_fields(field_dicts):
    """Takes a list of dicts that have Field attributes and
    returns a dictionary where they keys are names of fields
    and the values are the fields themselves."""
    return {k.lower(): Field(**v) for k, v in field_dicts.items()}


def create_clean_template(template_dict):
    """Takes a dictionary that has Template attributes
    and removes all attributes that the frontend does not need.
    Transforms the list of Field dicts into a list of their names."""
    cleaned = template_dict.copy()
    cleaned.pop('path', None)
    signature = cleaned.pop('signature', False)
    field_dicts = cleaned['fields']
    cleaned['fields'] = [{'name': k} for k in field_dicts]
    cleaned['signature'] = bool(signature)
    return cleaned


def frontend_templates_as_json():
    """Returns the frontend-friendly JSON version of all valid templates.
    They look like this:
    {
        "template name" : {
            "signature" : true,
            "fields" : ["first field", "second field"]
        }
    }
    """
    dicts = load_json_from(os.path.join(TEMPLATE_FOLDER, TEMPLATE_FILE))
    valid = discard_nonexistant_templates(dicts)
    return dumps({k: create_clean_template(v) for k, v in valid.items()})


def frontend_signatures_as_json():
    """Returns the frontend-friendly JSON for all valid signatures"""
    dicts = load_json_from(os.path.join(SIGNATURE_FOLDER, SIGNATURE_FILE))
    valid = discard_nonexistant_signatures(dicts)
    return dumps(valid)


def import_templates():
    """Returns a dictionary where the keys are template names
    and the values are the actual Template instances.
    """
    dicts = load_json_from(os.path.join(TEMPLATE_FOLDER, TEMPLATE_FILE))
    valid = discard_nonexistant_templates(dicts)

    for d in valid.values():
        d['path'] = os.path.join(TEMPLATE_FOLDER, d['path'])
    return {k.lower(): Template(**v) for k, v in valid.items()}
