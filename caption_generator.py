from nider.core import Font
from nider.core import Outline

from nider.models import Header
from nider.models import Paragraph
from nider.models import Linkback
from nider.models import Content
from nider.models import Image

from PIL import Image as PilImage


def generate_image_with_caption(input_path, result_path, caption):
    img = PilImage.open(input_path)
    width, height = img.size
    rgb_im = img.convert('RGB')
    rgb_im.save(input_path)

    text_outline = Outline(int(width / 1000), '#111')

    header = Header(
        text=caption,
        font=Font('impact.ttf', int(width / 12)),
        text_width=24,
        align='center',
        color='#ededed',
        outline=text_outline,
    )

    content = Content(header=header)

    result = Image(content,
                   fullpath=result_path,
                   width=width,
                   height=height
                   )

    result.draw_on_image(input_path)
