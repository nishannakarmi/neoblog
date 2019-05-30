from django.contrib import admin

# Register your models here.

from blog.models import Category, Blog, Comment, Profile


class BlogCommentInline(admin.TabularInline):
    model = Comment
    max_num = 0


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'get_likes_count', 'get_dislikes_count', 'category']
    inlines = [BlogCommentInline]
    list_filter = ('is_published',)


admin.site.register(Category)
# admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(Profile)
