from django.shortcuts import render, HttpResponse, redirect
# Create your views here.
from django.http import JsonResponse
from django.contrib import auth
from blog.froms import *
from django.db.models import Count,F
from django.db import transaction
from .models import *
import json
from cnblog import settings

# 登录
def login(request):
    if request.is_ajax():
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        valid_code = request.POST.get("valid_code")
        valid_str = request.session.get("valid_str")
        ret = {"state": False, "msg": None}
        if valid_code.upper() == valid_str.upper():
            user = auth.authenticate(username=user, password=pwd)
            if user:
                ret["state"] = True
                auth.login(request, user)
            else:
                ret["msg"] = "userinfo or pwd error"
        else:
            ret["msg"] = "验证码错误"
        return JsonResponse(ret)
    return render(request, "login.html")


# 验证码
def get_valid_img(request):
    from PIL import Image
    from PIL import ImageDraw, ImageFont
    import random
    def get_random_color():
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    image = Image.new("RGB", (250, 40), get_random_color())

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("static/font/man.ttf", size=26)
    tmp_list = []
    for i in range(5):
        u = chr(random.randint(65, 90))  # 生成大写字母
        l = chr(random.randint(97, 122))  # 生成小写字母
        n = str(random.randint(0, 9))  # 生成数字，注意要转换成字符串类型

        tmp = random.choice([u, l, n])
        tmp_list.append(tmp)
        draw.text((24 + i * 36, 0), tmp, fill=get_random_color(), font=font)
    # 加干扰线
    width = 220  # 图片宽度（防止越界）
    height = 35
    for i in range(5):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=get_random_color())

    # 加干扰点
    for i in range(40):
        draw.point((random.randint(0, width), random.randint(0, height)), fill=get_random_color())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())
    # 方式一
    # f= open("valid_code.png", "wb")
    # image.save(f, "png")
    # f= open("valid_code.png", "rb")
    # data = f.read()
    # f.close()

    # 方式二
    # from io import BytesIO
    # f = BytesIO()
    # image.save(f,"png")
    # data = f.getvalue()
    # f.close()
    #
    # 方式三加上随机字符串
    from io import BytesIO
    f = BytesIO()
    image.save(f, "png")
    data = f.getvalue()
    f.close()

    valid_str = "".join(tmp_list)
    request.session["valid_str"] = valid_str

    return HttpResponse(data)


# 注册
def reg(request):
    if request.method == "POST":
        res = {"user": None, "error_dict": None}
        form = RegForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get("user")
            pwd = form.cleaned_data.get("pwd")
            email = form.cleaned_data.get("email")
            avatar = request.FILES.get("avatar")
            # print("user", user)
            if avatar:
                UserInfo.objects.create_user(username=user, password=pwd, email=email, avatar=avatar)
            else:
                UserInfo.objects.create_user(username=user, password=pwd, email=email)
            res["user"]=1
        else:
            res["error_dict"] = form.errors
        return JsonResponse(res)
    form = RegForm()
    return render(request, "reg.html", {"form":form})


# 注销
def logout(request):
    auth.logout(request)
    return redirect("/index/")


# 修改密码
def change_password(request):
    if request.method == "POST":
        res = {"user": None, "error_dict": None}
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        new_pwd = request.POST.get("new_pwd")
        repeat_new_pwd = request.POST.get("repeat_new_pwd")
        user_obj = auth.authenticate(username=user, password=pwd)
        if user_obj is not None:
            if new_pwd == repeat_new_pwd and len(pwd) > 4:
                user_obj.set_password(new_pwd)
                user_obj.save()
                res["user"] = 1
            else:
                res["error_dict"] = "两次密码不一致"
        else:
            res["error_dict"] = "原密码不正确"
        return JsonResponse(res)
    return render(request, "change_password.html")


# 修改头像
def modify_avatar(request):
    if request.method == "POST":
        res = {"user": None}
        user = request.POST.get("user")
        avatar = request.FILES.get("avatar")
        print(avatar)
        user_obj = UserInfo.objects.get(username=user)
        user_obj.avatar = avatar
        user_obj.save()
        res["user"] = 1
        return JsonResponse(res)
    return render(request, "modify_avatar.html")


# 首页
def index(request):
    article_list = Article.objects.all()
    # 查询当前站点的所有分类
    cate_list = Category.objects.all().annotate(c=Count("article")).values_list("title", "c")
    # 查询当前站点的所有标签
    tag_list = Tag.objects.all().annotate(c=Count("article")).values_list("title", "c")
    # 查询当前站点的年月对应的文章数
    date_list = Article.objects.all().extra(
        select={"create_ym": "DATE_FORMAT(create_time,'%%Y-%%m')"}).values("create_ym").annotate(
        c=Count("*")).values_list("create_ym", "c")
    return render(request, "index.html", {"article_list":article_list, "cate_list": cate_list, "tag_list": tag_list,  "date_list": date_list})


# 个人站点
def homesite(request, username, **kwargs):
    print(username)
    # 站点用户对象
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse(404)
    # 当前站点对象
    blog = user.blog
    # 查询当前站点的所有文章
    if not kwargs:
        article_list = Article.objects.filter(user=user)
    else:
        condition = kwargs.get("condition")
        param = kwargs.get("param")
        if condition == "cate":
            article_list = Article.objects.filter(user=user).filter(category__title=param)
        elif condition == "tag":
            article_list = Article.objects.filter(user=user).filter(tags__title=param)
        else:
            year, month = param.split("-")
            article_list = Article.objects.filter(user=user).filter(create_time__year=year)
    return render(request, "homesite.html", locals())


# 文章详情页面
def article_detail(request, username, article_id):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    article = Article.objects.filter(pk=article_id).first()
    # 所有评论列表
    comment_list = Comment.objects.filter(article_id=article_id)
    return render(request, "article_detail.html", locals())


# 点赞踩灭
def poll(request):
    print(request.POST)
    is_up = json.loads(request.POST.get("is_up"))
    article_id = request.POST.get("article_id")
    user_id = request.user.pk
    res = {"state":True}
    try:
        with transaction.atomic():
            ArticleUpDown.objects.create(is_up=is_up, article_id=article_id, user_id=user_id)
            if is_up:
                Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
            else:
                Article.objects.filter(pk=article_id).update(down_count=F("down_count")+1)
    except Exception as e:
        res["state"] = False
        res["fisrt_action"]=ArticleUpDown.objects.filter(user_id=user_id,article_id=article_id).first().is_up
    return JsonResponse(res)


# 提交评论
def comment(request):
    print(request.POST)
    pid = request.POST.get("pid")
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    user_pk = request.user.pk
    response = {}
    with transaction.atomic():
        if not pid:  # 根评论
            comment_obj = Comment.objects.create(article_id=article_id, user_id=user_pk, content=content)
        else:
            comment_obj = Comment.objects.create(article_id=article_id, user_id=user_pk, content=content, parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)

    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d")
    response["content"] = comment_obj.content
    response["username"] = comment_obj.user.username

    return JsonResponse(response)


# 获取评论数据
def get_comment_tree(request, id):
    ret = list(Comment.objects.filter(article_id=id).values("pk", "content", "parent_comment_id", "user__username"))
    print(ret)
    return JsonResponse(ret, safe=False)


# 个人管理后台
def backend(request):
    article_list = Article.objects.filter(user=request.user)
    return render(request, "backend.html", locals())


# 添加文章
def add_article(request):
    if request.method == "POST":
        title = request.POST.get("title")
        article_con = request.POST.get("article_con")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(article_con,"html.parser")
        # 过滤
        for tag in soup.find_all():
            if tag.name == "script":
                tag.decompose()
        article_obj = Article.objects.create(title=title, user=request.user, desc=soup.text[0:150])
        ArticleDetail.objects.create(content=soup.prettify(), article=article_obj)
        return redirect("/blog/backend/")
    else:
        return render(request, "add_article.html")


# 文件上传
def upload_img(request):
    img_obj = request.FILES.get("imgFile")
    import os
    media_path = settings.MEDIA_ROOT
    path = os.path.join(media_path,"article_imgs",img_obj.name)
    with open(path, 'wb') as f:
        for line in img_obj:
            f.write(line)
    res = {
        "url":"/media/article_imgs/"+img_obj.name,
        "error":0
    }
    import json
    return HttpResponse(json.dumps(res))


# 删除文章
def delete_article(request):
    nid = request.GET.get("id")
    del_obj = Article.objects.filter(nid=nid)
    del_obj.delete()
    return redirect("/blog/backend/")


# 编辑文章
def edit_article(request):
    nid = request.GET.get("id")
    edit_article_obj = Article.objects.get(nid=nid)
    if request.method == "POST":
        title = request.POST.get("title")
        article_con = request.POST.get("article_con")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(article_con, "html.parser")
        # 过滤
        for tag in soup.find_all():
            if tag.name == "script":
                tag.decompose()
        edit_article_obj.title = title
        edit_article_obj.desc = soup.text[0:150]
        edit_articledetail_obj = ArticleDetail.objects.get(article_id=nid)
        edit_articledetail_obj.content = soup.prettify()
        edit_article_obj.save()
        edit_articledetail_obj.save()
        return redirect("/blog/backend/")
    return render(request, "edit_article.html", locals())