from django.contrib import admin
from .models import Link, Post, Comment, Tag, Token, HotLink, Media, Setting


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('user', 'image','title', 'description', 'slug', 'text', 'is_pub', 'tags')}),
     )

    list_display = ('title','user', 'date', 'is_pub')
    list_filter = ('is_pub',)
    search_fields = ('title', 'slug')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'post')

admin.site.register(Tag)
admin.site.register(Link)
admin.site.register(Token)
admin.site.register(HotLink)
admin.site.register(Media)
admin.site.register(Setting)