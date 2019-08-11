from django import template
from blog.models import *
register = template.Library()


@register.inclusion_tag("menu.html")
def get_menu(username):
    user = UserInfo.objects.filter(username=username).first()
    # 当前站点对象
    blog = user.blog
    from django.db.models import Count
    # 查询当前站点的所有分类
    # cate_list = Category.objects.filter(blog=blog)
    # from django.db.models import Count
    cate_list = Category.objects.filter(blog=blog) \
        .annotate(c=Count("article")).values_list("title", "c")
    # 查询当前站点的所有标签
    tag_list = Tag.objects.filter(blog=blog).annotate(c=Count("article")).values_list("title", "c")

    # 查询当前站点的年月对应的文章数
    date_list = Article.objects.filter(user=user).extra(
        select={"create_ym": "DATE_FORMAT(create_time,'%%Y-%%m')"}).values("create_ym").annotate(
        c=Count("*")).values_list("create_ym", "c")

    return {"blog": blog, "username": username, "cate_list": cate_list, "tag_list": tag_list, "date_list": date_list}
