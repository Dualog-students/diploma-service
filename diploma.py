from template import import_templates
from PIL import Image, ImageDraw, ImageFont, ImageColor

FONT_NAME = 'DejaVuSans.ttf'


class UnknownFields(ValueError):
    pass


class MissingFields(ValueError):
    pass


def draw_box_with_name(context, size, field, name):
    """Draws a rectangle where the field should be placed"""
    rect = get_rect(field, size)
    color = faded_background = ImageColor.getrgb(field.color)
    if len(color) == 4:
        # Fade the text color if possible
        faded_background = color[0:2] + color[3] / 4
    else:
        # Transparent white
        faded_background = (255, 255, 255, 64)
    context.rectangle(rect, outline=color, fill=faded_background)

    font = get_font_that_fits_in_box(name, rect)
    center = center_text_in_rect(font.getsize(name), rect)
    context.text(center, name, font=font, fill=ImageColor.getrgb(field.color))


def get_font_that_fits_in_box(text, rect):
    """Returns a font that can be used to draw text into a given rect
    without overflowing its boundaries."""
    x1, y1, x2, y2 = rect
    width = x2 - x1
    height = y2 - y1
    fontsize = 1
    # Dirty hack to find the largest text we can fit in this box
    font = ImageFont.truetype(FONT_NAME, fontsize)
    while font.getsize(text)[1] < height and font.getsize(text)[0] < width:
        fontsize += 1
        font = ImageFont.truetype(FONT_NAME, fontsize)
    fontsize -= 1
    return ImageFont.truetype(FONT_NAME, fontsize)


def get_rect(field, size):
    """Returns two points that define the upper left and bottom right points
    in a rectangle for the given field."""
    width, height = size
    x1 = int(width * field.x)
    y1 = int(height * field.y)
    x2 = x1 + int(width * field.w)
    y2 = y1 + int(height * field.h)

    return (x1, y1, x2, y2)


def center_text_in_rect(textsize, rect):
    w, h = textsize
    x1, y1, x2, y2 = rect
    rect_w, rect_h = x2 - x1, y2 - y1
    return (x1 + (rect_w - w) / 2, y1 + (rect_h - h) / 2)


def draw_centered_full_size(context, size, field):
    """Draws the provided fields value onto the context.
    The value will be centered and shown using using the largest
    font size that won't overflow its bounding box."""
    text = field.value
    rect = get_rect(field, size)
    font = get_font_that_fits_in_box(text, rect[:2])
    center = center_text_in_rect(font.getsize(text), rect)
    context.text(center, field.value, font=font, fill=ImageColor.getrgb(field.color))


def draw_scaled_signature(image, signature):
    """Draws the signature field onto the image.
    The signature will be scaled to fit into its area
    while preserving its aspect ratio."""
    rect = get_rect(signature, image.size)
    signature = Image \
        .open(signature.value) \
        .convert('RGBA')
    signature.thumbnail(rect[:2])
    image.paste(signature, box=rect[:2])


def create_diploma_image(template):
    """Turns a valid template into a PNG image diploma by drawing
    the fields (and signature, if applicable) onto the template base
    """
    base_template = Image.open(template.path).convert('RGBA')
    text = Image.new('RGBA', base_template.size, (255, 255, 255, 0))
    context = ImageDraw.Draw(text)

    for name, field in template.fields.items():
        draw_centered_full_size(context, base_template.size, field)

    if template.signature and template.signature.value:
        draw_scaled_signature(text, template.signature)

    return Image.alpha_composite(base_template, text)


def create_template_preview(template, size=None):
    """Creates a preview version of the template where all fields are
    marked with a semi-transparent rectangle containing the field name.
    If the size argument is provided the it is used to constrain
    the size of the image while preserving aspect ratio.
    """
    base_template = Image.open(template.path).convert('RGBA')
    if size:
        base_template.thumbnail(size)
    text = Image.new('RGBA', base_template.size, (255, 255, 255, 0))
    context = ImageDraw.Draw(text)

    for name, field in template.fields.items():
        draw_box_with_name(context, base_template.size, field, name)

    if template.signature is not None:
        draw_box_with_name(context, base_template.size, template.signature, 'signature')

    return Image.alpha_composite(base_template, text)


def create_signature_preview(signature, size):
    """Creates a preview version of the signature. The signature is overlaid
    onto a white background because we assume the lines will be colored.
    If the size argument is provided the it is used to constrain
    the size of the image while preserving aspect ratio.
    """
    base_signature = Image.open(signature).convert('RGBA')
    if size:
        base_signature.thumbnail(size)
    background = Image.new('RGBA', base_signature.size, (255, 255, 255, 255))
    return Image.alpha_composite(background, base_signature)


def generate_diploma(template_name, **fields):
    """Creates a diploma by matching the items in the fields
    dictionary to the values contained in the template. Raises MissingFields
    if the dict does not contain all of the required fields and KeyError
    if the dictionary contains a field that does not fit into this template.
    Returns an instance of PIL.Image."""
    t = import_templates()[template_name]

    path = fields.pop('signature', None)
    if path and t.signature is not None:
        t.signature = path

    for k, v in fields.items():
        t.fields[k].value = v

    if not t.valid and t.empty_fields:
        raise MissingFields(','.join(t.empty_fields))

    return create_diploma_image(t)


def preview_template(template_name, size):
    template = import_templates()[template_name]
    return create_template_preview(template, size)


def preview_signature(signature_path, size):
    return create_signature_preview(signature_path, size)
