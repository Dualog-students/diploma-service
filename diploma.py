from template import import_templates
from PIL import Image, ImageDraw, ImageFont, ImageColor


class UnknownFields(ValueError):
    pass


class MissingFields(ValueError):
    pass


def draw_box_with_name(context, size, field, name):
    width, height = size
    x1 = int(width * field.x)
    y1 = int(height * field.y)
    x2 = x1 + int(width * field.w)
    y2 = y1 + int(height * field.h)
    bounding_box = ((x1, y1), (x2, y2))
    color = faded_background = ImageColor.getrgb(field.color)
    if len(color) == 4:
        faded_background = color[0:2] + color[3] / 2
    else:
        faded_background = (255, 255, 255, 96)
    context.rectangle(bounding_box, outline=color, fill=faded_background)
    fontsize = 1
    # Dirty hack to find the largest text we can fit in this box
    font = ImageFont.truetype('DejaVuSans.ttf', fontsize)
    while font.getsize(name)[1] < field.h * height and font.getsize(name)[0] < field.w * width:
        fontsize += 1
        font = ImageFont.truetype('DejaVuSans.ttf', fontsize)
    fontsize -= 1
    font = ImageFont.truetype('DejaVuSans.ttf', fontsize)
    text_width, text_height = font.getsize(name)
    center = (x1 + (x2 - x1 - text_width) / 2, y1 + (y2 - y1 - text_height) / 2)
    context.text(center, name, font=font, fill=ImageColor.getrgb(field.color))


def draw_centered_full_size(context, size, field):
    width, height = size
    text = field.value
    box_width = int(width * field.w)
    box_height = int(height * field.h)
    box_x = int(width * field.x)
    box_y = int(height * field.y)
    fontsize = 1
    # Dirty hack to find the largest text we can fit in this box
    font = ImageFont.truetype('DejaVuSans.ttf', fontsize)
    while font.getsize(text)[1] < field.h * height and font.getsize(text)[0] < field.w * width:
        fontsize += 1
        font = ImageFont.truetype('DejaVuSans.ttf', fontsize)
    fontsize -= 1
    font = ImageFont.truetype('DejaVuSans.ttf', fontsize)

    text_width, text_height = font.getsize(text)
    center = (box_x + (box_width - text_width) / 2, box_y + (box_height - text_height) / 2)
    context.text(center, field.value, font=font, fill=ImageColor.getrgb(field.color))


def draw_scaled_signature(text, size, signature):
    width, height = size
    box_width = int(width * signature.w)
    box_height = int(height * signature.h)
    box_x = int(width * signature.x)
    box_y = int(height * signature.y)
    signature = Image \
        .open(signature.value) \
        .convert('RGBA')
    signature.thumbnail((box_width, box_height))
    text.paste(signature, box=(box_x, box_y))


def create_diploma_image(template):
    base_template = Image.open(template.path).convert('RGBA')
    text = Image.new('RGBA', base_template.size, (255, 255, 255, 0))
    context = ImageDraw.Draw(text)

    for name, field in template.fields.items():
        draw_centered_full_size(context, base_template.size, field)

    if template.signature and template.signature.value:
        draw_scaled_signature(text, base_template.size, template.signature)

    return Image.alpha_composite(base_template, text)


def create_template_preview(template, size):
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
    base_signature = Image.open(signature).convert('RGBA')
    if size:
        base_signature.thumbnail(size)
    background = Image.new('RGBA', base_signature.size, (255, 255, 255, 255))
    return Image.alpha_composite(background, base_signature)


def generate_diploma(template_name, **fields):
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
