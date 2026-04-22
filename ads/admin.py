from django.contrib import admin
from .models import Category, Ad, AdInfo

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')

@admin.register(AdInfo)
class AdInfoAdmin(admin.ModelAdmin):
    list_display = ('ad', 'views_count', 'likes_count')