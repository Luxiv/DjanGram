from django.contrib import admin
from .models import UserAccount, Article


class UserAccountAdmin(admin.ModelAdmin):
    pass
    # prepopulated_fields = {'slug': ('username', )}


class ArticleAdmin(admin.ModelAdmin):
    pass
    # prepopulated_fields = {'slug': ('title', )}


admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(Article, ArticleAdmin)
