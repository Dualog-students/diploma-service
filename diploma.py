from template import import_templates
from PIL import Image, ImageDraw, ImageFont, ImageColor


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


def create_diploma_image(template):
    base_template = Image.open(template.path).convert('RGBA')
    text = Image.new('RGBA', base_template.size, (255, 255, 255, 0))
    context = ImageDraw.Draw(text)

    for field in template.fields.values():
        draw_centered_full_size(context, base_template.size, field)

    return Image.alpha_composite(base_template, text)


def generate_diploma(template_name, **fields):
    t = import_templates('templates/templates.json')[template_name]
    for k, v in fields.items():
        t.fields[k].value = v

    if not t.valid:
        raise ValueError(','.join(t.missing))

    return create_diploma_image(t)
