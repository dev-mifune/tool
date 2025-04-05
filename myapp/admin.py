from django.contrib import admin
from .models import Category, Task

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'due_date', 'created_at', 'updated_at')
    list_filter = ('status', 'category', 'due_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
