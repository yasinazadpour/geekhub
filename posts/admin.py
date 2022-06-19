from django.contrib import admin
from .models import Link, Post, Comment, Tag, Token


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'date', 'is_pub')
    list_filter = ('is_pub',)
    search_fields = ('title', 'slug')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'post')

admin.site.register(Tag)
admin.site.register(Link)
admin.site.register(Token)