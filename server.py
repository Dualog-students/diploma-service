from io import BytesIO
from flask import Flask, send_file, request
from diploma import generate_diploma
from template import valid_template_names

app = Flask(__name__)


def serve_diploma_image(diploma_image):
    iostream = BytesIO()
    diploma_image.save(iostream, 'PNG')
    iostream.seek(0)
    return send_file(iostream, mimetype='image/png')


@app.route('/<template_name>')
def serve_diploma(template_name):
    template_name = template_name.lower()
    if template_name not in valid_template_names():
        return my404('whoops')

    kwargs = {k: " ".join(v) for k, v in dict(request.args).items()}
    dip = generate_diploma(template_name, **kwargs)
    return serve_diploma_image(dip)


@app.errorhandler(404)
def my404(error):
    return """OOPSIE WOOPSIE!!<br><br>

    Uwu We made a fucky wucky!! A wittle fucko boingo!<br>
    The code monkeys at our headquarters are working VEWY HAWD to fix this!
    """


@app.errorhandler(Exception)
def generic(error):
    return repr(error)
