from django import template
from blog import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

register = template.Library()


@register.inclusion_tag("left_menu.html")
def left_menu(username):
    tag_list = models.Tag.objects.filter(article__author__username=username).\
        annotate(number=Count('pk')).values_list("name", "number", "id")
    category_list = models.Category.objects.filter(article__author__username=username).\
        annotate(number=Count('pk')).values_list("name", "number", "id")
    create_list = models.Article.objects.filter(author__username=username).annotate(month=TruncMonth('create_time')).\
        values('month').annotate(number=Count('id')).values_list('month', 'number')
    return locals()


@register.simple_tag
def get_comment_obj(nid):
    try:
        obj = models.Comment.objects.get(id=int(nid))
        print(nid)
        return obj
    except:
        return ''


@register.simple_tag
def test(x):
    print(x)
    return x