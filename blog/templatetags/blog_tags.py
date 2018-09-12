from django import template
from tagging.models import Tag
from random import choice

from blog.models import Post

register = template.Library()


@register.simple_tag
def get_tags():
    tag_list = Tag.objects.cloud_for_model(model=Post, steps=4)
    for tag in tag_list:
        tag.font_size = 5 + (tag.font_size)*3
    # 排序并限量
    print(type(tag_list))
    result = []
    for i in range(12):
        temp = choice(tag_list)
        tag_list.remove(temp)
        result.append(temp)
        if not tag_list:
            break
    return result