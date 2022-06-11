from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from blog import forms, models
from PIL import Image, ImageDraw, ImageFont
import random
import string
from io import BytesIO
from django.contrib import auth
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from BBS2 import settings


def register(request):
    ret = {'status': 1, 'message': ''}
    if request.method == 'POST':
        reg_form = forms.RegForm(request.POST)
        if reg_form.is_valid():
            clean_data = reg_form.cleaned_data
            clean_data.pop('password2')
            # 用户是否上传头像，关键
            if request.FILES.get('avatar'):
                clean_data['avatar'] = request.FILES['avatar']
            user = models.UserInfo.objects.create_user(**clean_data)
            ret['message'] = '注册成功'
            ret['url'] = '/login/'
        else:
            ret['status'] = 0
            ret['message'] = reg_form.errors
        return JsonResponse(ret)
    else:
        reg_form = forms.RegForm()
    return render(request, 'register.html', {'form': reg_form})


def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        ret = {'status': 1, 'message': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        if request.session.get('code').lower() == code.lower():
            user_obj = auth.authenticate(username=username, password=password)
            if user_obj:
                auth.login(request, user_obj)
                return redirect('/home')
            else:
                ret['status'] = 0
                ret['message'] = '用户名或密码错误'
        else:
            ret['status'] = 0
            ret['message'] = '验证码错误'
        return JsonResponse(ret)
    return render(request, 'login.html')


def get_random():
    return random.randint(1, 255), random.randint(1, 255), random.randint(1, 255),


def get_code(request):
    # with open(r'static/img/3v3.png', 'rb') as f:
    #     data = f.read()
    # img = Image.new('RGB', (100, 100), get_random())
    # with open('xxx', 'wb') as f:
    #     img.save(f, 'png')
    # with open('xxx', 'rb') as f:
    #     data = f.read()
    # 频繁读取，效率低

    img = Image.new('RGB', (100, 100), 'white')
    img_draw = ImageDraw.Draw(img)
    img_font = ImageFont.truetype('/static/fonts/tahoma.ttf', 35)  # 字体样式
    code = ''
    for i in range(4):
        x = random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
        img_draw.text((i*20+10, 20), x, get_random(), img_font)
        code += x
    print(code)
    # 存入session中
    request.session['code'] = code
    io_obj = BytesIO()
    img.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def home(request):
    article_list = models.Article.objects.all().order_by("-create_time")
    paginator = Paginator(article_list, settings.NUM_PER_PAGE)
    page = request.GET.get("page",1)
    try:
        query_sets = paginator.page(page)
    except PageNotAnInteger:
        query_sets = paginator.page(1)
    except EmptyPage:
        query_sets = paginator.page(paginator.num_pages)
        page = paginator.num_pages
    current_page = query_sets.number
    page_list = paginator.get_elided_page_range(page)
    return render(request, "home.html", locals())


@login_required
def logout(request):
    auth.logout(request)
    return redirect('home')


@login_required
def reset_pwd(request):
    if request.method == 'POST':
        ret = {'status':1, 'message':0}
        origin_pwd = request.POST.get('origin_pwd')
        new_pwd = request.POST.get('new_pwd')
        confirm_pwd = request.POST.get('confirm_pwd')
        if request.user.check_password(origin_pwd):
            if new_pwd == confirm_pwd:
                request.user.set_password(new_pwd)
                request.user.save()
            else:
                ret['status'] = 0
                ret['message'] = '两次密码不一致'
        else:
            ret['status'] = 0
            ret['message'] = '原密码输入有误'
        return JsonResponse(ret)
    return HttpResponse('ok')


def site(request, username, **kwargs):
    blog = models.Blog.objects.filter(userinfo__username=username).first()
    if not blog:
        return render(request, '404.html')
    article_list = models.Article.objects.filter(author__username=username)
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'tag':
            article_list = article_list.filter(tags__id=param)
        elif condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'archive':
            year, month = param.split('-')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
    return render(request, 'site.html', locals())


def article(request, username, article_id):
    """

    :param request:
    :param username:
    :param article_id:
    :return:
    构造评论树
    {
    comment1.id:{"children":[comment2.id:{children:[]},comment3.id:{}],"parent":3},
    comment4.id:{...},
    }
    """
    article = models.Article.objects.filter(id=article_id).first()
    username = username
    comments = article.comment_set.all().order_by("-comment_time")
    # 因为评论应该是有序的，因此需要用列表而不是字典存储所有的评论
    comment_list = []
    for comment in comments:
        # 构造一个基本格式
        # {'1': {'content': '', 'children': [], 'parent': None}}
        comment_dict = {str(comment.id): {}}
        comment_dict[str(comment.id)]["content"] = comment.content
        comment_dict[str(comment.id)]["avatar"] = '/media/%s' % comment.user.avatar
        comment_dict[str(comment.id)]["comment_time"] = comment.comment_time.strftime("%Y-%m-%d %H:%M:%S")
        comment_dict[str(comment.id)]["username"] = comment.user.username
        comment_dict[str(comment.id)]["children"] = []
        comment_dict[str(comment.id)]["parent"] = comment.parent_comment_id
        if not comment.parent_comment_id:
            comment_dict[str(comment.id)]["parent"] = ''
        comment_list.append(comment_dict)
    comment_tree = []
    for item in comment_list:
        # item是一个字典
        for k, v in item.items():
            if not v['parent']:
                # 没有父亲，这是根评论
                comment_tree.append(item)
            else:
                # 子评论，需要加入父亲的children列表
                # 由于是按照时间倒序排列，子评论一定先出现在父评论之前，因此可以直接去comment_list寻找父亲
                # 一定是子评论全部append完成，才会扫到父评论
                # 首先要找到父亲,列表只能遍历？
                for i in comment_list:
                    for key, value in i.items():
                        if key == str(v['parent']):
                            # 找到之后加入
                            value["children"].append(item)
    import pprint
    # pprint.pprint(comment_tree)
    # 为了加载css必须传入blog参数
    blog = models.Blog.objects.filter(userinfo__username=username).first()
    return render(request, 'article.html', locals())


@login_required
def backend(request, username):
    username = username
    return render(request, "backend.html", locals())


@login_required
def add_article(request, username):
    username = username
    tag_list = models.Tag.objects.filter(article__author__username=username).distinct()
    category_list = models.Category.objects.filter(article__author__username=username).distinct()
    if request.method=='POST':
        title=request.POST.get("title")
        content=request.POST.get("content")
        # 使用bs4模块找出前50个字符（不包含标签）
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()
        summary=soup.text[:100]
        category_id = request.POST.get("category")
        tags = request.POST.getlist("tag")
        article = models.Article.objects.create(
            title=title,
            content=str(soup),
            summary=summary,
            author=models.UserInfo.objects.filter(username=username).first(),
            category_id=category_id)
        article.tags.add(*tags)
        return redirect('/home')
    return render(request, "add_article.html", locals())


@xframe_options_exempt
def upload_img(request):
    print('hahaah')
    return HttpResponse('ok')


@login_required
def click_favor(request):
    if request.method == 'POST':
        ret = {'msg': ''}
        article_id = request.POST.get("article_id")
        ret['current_num'] = models.Article.objects.get(id=article_id).favor_set.count()
        is_clicked = models.Favor.objects.filter(article_id=article_id, user_id=request.user.id).exists()
        if not is_clicked:
            models.Favor.objects.create(article_id=article_id, user_id=request.user.id)
            ret['msg'] = '点赞成功'
            ret['current_num'] += 1
            ret['status'] = 1
        else:
            models.Favor.objects.filter(article_id=article_id, user_id=request.user.id).delete()
            ret['msg'] = '您已取消点赞'
            ret['current_num'] -= 1
            ret['status'] = 0
        return JsonResponse(ret)
    return HttpResponse('ok')


@login_required
def comment(request):
    ret = {}
    article_id = request.POST.get("article_id")
    # 获取跟评论数量
    root_comment = models.Comment.objects.filter(article_id=article_id).filter(parent_comment=None).count()
    comment_content = request.POST.get("content")
    # 获取父评论id
    parent_id = request.POST.get("parent_id")
    print(parent_id)
    user_id = request.user.id
    comment = models.Comment.objects.create(
        user_id=user_id,
        article_id=article_id,
        content=comment_content,
        parent_comment_id=parent_id,
    )
    # 返回评论时间与楼层数，用于前段渲染
    comment_time = comment.comment_time.strftime("%Y-%m-%d %H:%M:%S")
    ret['root_comment'] = root_comment+1 if not parent_id else root_comment
    # 获取评论时间
    ret['comment_time'] = comment_time
    # 该条评论的id
    ret['comment_id'] = comment.id
    return JsonResponse(ret)


@login_required
def change_avatar(request, username):
    if request.method == 'POST':
        img = request.FILES.get('new-avatar')
        # 更新方式一
        # models.UserInfo.objects.filter().update(avatar=img)
        # 上面的方式不会自动为头像增加'avatar/'前缀

        # 更新方式二
        # user = models.UserInfo.objects.filter(username=username).first()
        user = request.user
        user.avatar = img
        user.save()
        return redirect('/home')
    return render(request, "change_avatar.html")