from django.contrib import admin
from .models import Category, Tag, Ad, Comment, Favorite


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'slug']
    list_filter = ['type']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['author', 'created_at']


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'price', 'city', 'status', 'is_active', 'views_count', 'created_at']
    list_filter = ['status', 'is_active', 'category', 'created_at']
    search_fields = ['title', 'description', 'author__username', 'city']
    list_editable = ['is_active', 'status']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    filter_horizontal = ['tags']
    inlines = [CommentInline]
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'ad', 'created_at']
    search_fields = ['author__username', 'text']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'ad', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'ad__title']
