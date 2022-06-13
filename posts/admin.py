from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'date', 'is_pub')
    list_filter = ('is_pub',)
    search_fields = ('title', 'slug')
