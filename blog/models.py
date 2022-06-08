from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class UserInfo(AbstractUser):
    """用户表"""
    email = models.EmailField(verbose_name="邮箱", blank=True, null=True)
    avatar = models.FileField(
        verbose_name="用户头像",
        upload_to='avatar/',
        default='avatar/default.png',
        )
    blog = models.OneToOneField("Blog", on_delete=models.CASCADE, blank=True, null=True)


class Blog(models.Model):
    """个人站点表"""
    site_name = models.CharField(verbose_name="站点名称", max_length=32)
    site_title = models.CharField(verbose_name="站点标题", max_length=32)
    site_theme = models.CharField(verbose_name="站点主题", max_length=128)

    def __str__(self):
        return self.site_name


class Article(models.Model):
    """文章表"""
    title = models.CharField(verbose_name="标题", max_length=64)
    summary = models.CharField(verbose_name="摘要", max_length=128)
    content = models.TextField(verbose_name="文章内容")
    create_time = models.DateField(verbose_name="创建时间", auto_now_add=True)
    author = models.ForeignKey("UserInfo", related_name="articles", on_delete=models.CASCADE)
    tags = models.ManyToManyField("Tag")
    category = models.ForeignKey("Category", on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(verbose_name="文章标签", max_length=16)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(verbose_name="文章分类", max_length=16)

    def __str__(self):
        return self.name


class Favor(models.Model):
    article = models.ForeignKey("Article", on_delete=models.CASCADE)
    user = models.ForeignKey("UserInfo", on_delete=models.CASCADE)


class Comment(models.Model):
    user = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    article = models.ForeignKey("Article", on_delete=models.CASCADE)
    content = models.TextField(verbose_name="评论内容")
    comment_time = models.DateTimeField(verbose_name="评论时间", auto_now_add=True)
    parent_comment = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.content
