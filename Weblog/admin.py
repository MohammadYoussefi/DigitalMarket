from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish_date', 'status')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'publish_date')
    search_fields = ('title', 'content')


