from io import BytesIO
from flask import Flask, send_file, request
from json import dumps
from diploma import generate_diploma, UnknownFields, \
    MissingFields, preview_template, preview_signature
from template import import_templates, BadSignature, \
    frontend_templates_as_json, frontend_signatures_as_json
import os

app = Flask(__name__)


def get_size(width, height):
    if not (width or height):
        size = None
    elif not width and height:
        size = (height, height)
    elif not height and width:
        size = (width, width)
    else:
        size = (height, width)

    if size:
        size = tuple(int(dim) for dim in size)

    return size


def serve_image(diploma_image):
    iostream = BytesIO()
    diploma_image.save(iostream, 'PNG')
    iostream.seek(0)
    return send_file(iostream, mimetype='image/png')


@app.route('/<data>.json')
def serve_json_file(data):
    if data == "templates":
        return frontend_templates_as_json()
    elif data == "signatures":
        return frontend_signatures_as_json()

    return my404('not found')


@app.route('/preview/<filename>')
def serve_preview_image(filename):
    width = request.args.get('width', None)
    height = request.args.get('height', None)
    size = get_size(width, height)

    signature = f"signatures/{filename}.png"

    if filename in import_templates():
        return serve_image(preview_template(filename, size))
    if os.path.exists(signature):
        return serve_image(preview_signature(signature, size))
    else:
        return my404('whoops')


@app.route('/<template_name>')
def serve_diploma(template_name):
    template_name = template_name.lower()

    kwargs = {k: ' '.join(v) for k, v in dict(request.args).items()}
    finished_diploma = generate_diploma(template_name, **kwargs)
    return serve_image(finished_diploma)


@app.route('/favicon.ico')
def favicon():
    return send_file(
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


@app.errorhandler(BadSignature)
def bad_signature(error):
    payload = dumps({"bad_signature": str(error)})
    return (payload, 422, {"content-type": "application/json"})


@app.errorhandler(MissingFields)
def missing_query_params(error):
    missing_fields = str(error).split(',')
    payload = dumps({"missing_fields": missing_fields})
    return (payload, 422, {"content-type": "application/json"})


@app.errorhandler(UnknownFields)
def superfluous_query_params(error):
    superfluous_fields = str(error)[1:-1].split(',')
    payload = dumps({"superfluous_fields": superfluous_fields})
    return (payload, 422, {"content-type": "application/json"})


@app.errorhandler(404)
def my404(error):
    return '''OOPSIE WOOPSIE!!<br><br>

    Uwu We made a fucky wucky!! A wittle fucko boingo!<br>
    The code monkeys at our headquarters are working VEWY HAWD to fix this!
    '''
