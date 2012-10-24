#!/usr/bin/env python
#-*-coding=utf-8-*-

#******************************
# author:zhanghui9700@gmail.com
# date:201-10-24
# version:1.0
#******************************

import random
from cStringIO import StringIO
from PIL import Image,ImageDraw,ImageFont

from django.http import HttpResponse

FONT_PATH = "/opt/zhanghui/github/pykit/web/django/template/utils/Ubuntu-B.ttf"
FONT_SIZE = 20

def validate_image(request): 
    text = "1234"
    img_width,img_height = 80,28

    background = (random.randrange(230,255),\
                    random.randrange(230,255),\
                    random.randrange(230,255))
    line_color = (random.randrange(0,255),\
                    random.randrange(0,255),\
                    random.randrange(0,255))
    font_color = ["black","darkblue","darkred"]

    image = Image.new('RGB',(img_width,img_height),background)
    font = ImageFont.truetype(FONT_PATH,FONT_SIZE)
    draw = ImageDraw.Draw(image)

    for i in range(random.randrange(3,5)):
        xy = (random.randrange(0,img_width),random.randrange(0,img_height),\
              random.randrange(0,img_width),random.randrange(0,img_height))
        draw.line(xy,fill=line_color,width=1)

    draw.text((5,7),text,font=font,fill=random.choice(font_color))

    out = StringIO()
    image.save(out,"PNG")
    out.seek(0)
    
    response = HttpResponse()
    response['Content-Type'] = "image/png"
    response.write(out.read())

    return response
