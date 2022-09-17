from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class UserAccount(User, models.Model):
    slug = AutoSlugField(populate_from='username', db_index=True, unique=True, verbose_name='URL/Login')
    birth = models.DateField(verbose_name='Birth day', default=timezone.now)
    avatar = models.ImageField(upload_to='users/avatar', null=True, blank=True)
    about_user = models.TextField(verbose_name='Profile info', blank=True)
    friends = models.ManyToManyField('self', blank=True, symmetrical=False)
    User.email = models.EmailField(verbose_name='Email address', unique=True)
    email_verify = models.BooleanField(default=True)

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('profile', kwargs={'usr_slug': self.slug})


class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name='Tittle')
    slug = AutoSlugField(populate_from='title', unique=True, db_index=True, verbose_name='URL')
    content = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    creator = models.ForeignKey('UserAccount', on_delete=models.CASCADE,
                                blank=True, null=True, related_name='Author')
    likes = models.ManyToManyField('UserAccount', blank=True, related_name='Liked_Post')
    tags = TaggableManager()

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('post_view', kwargs={'post_slug': self.slug})

    class Meta:
        ordering = ['-time_create', 'title']


class Images(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField("photos/%Y/%m/%d")

    def __str__(self):
        return self.article.title
