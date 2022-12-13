from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
# Register your models here.
from django.contrib.admin import ModelAdmin
from django.utils.html import format_html

from apps import models
from apps.models import Post, Category, Comment, User


@admin.register(Post)
class Post(ModelAdmin):
    list_display = ('title', 'created_at', 'show_main_picture', 'category_set', 'status_choice', 'status_button')
    list_display_links = ('title', 'created_at')
    exclude = ("slug",)
    change_form_template = "admin/custom/change_form.html"

    def show_main_picture(self, obj):
        return format_html(f'<img src="{obj.main_picture.url}" style="width:200px; height:100px" >')

    def category_set(self, obj):
        return format_html(f'<b>{obj.category.first()} </b>')

    def status_choice(self, obj):
        data = {
            'pending': '<i class="fas fa-circle-notch fa-spin"></i>',
            'active': '<i class="fa-solid fa-check" style="color: green; font-size: 1em;margin-top: 8px; margin: auto;"></i>',
            'cancel': '<i class="fa-solid fa-circle-xmark"  style="color: red; font-size: 1em;margin-top: 8px; margin: auto;"></i>'
        }
        return format_html(data[obj.status])

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('cancel/<int:id>', self.cancel),
            path('active/<int:id>', self.active)]
        return urls + my_urls

    def active(self, request, id):
        post = models.Post.objects.filter(id=id).first()
        post.status = models.Post.Status.ACTIVE
        post.save_base()
        return HttpResponseRedirect('../')

    def cancel(self, request, id):
        post = models.Post.objects.filter(id=id).first()
        post.status = models.Post.Status.CANCEL
        post.save_base()
        return HttpResponseRedirect('../')


@admin.register(Category)
class Category(ModelAdmin):
    list_display = ('name',)
    exclude = ('slug',)

    # def show_image(self, obj):
    #     return format_html(f'<img src="{obj.image.url}" style="width:200px; height:100px" >')


@admin.register(Comment)
class Comment(ModelAdmin):
    list_display = ('author', 'created_at', 'comment', 'blog')


@admin.register(User)
class User(ModelAdmin):
    list_display = ('username', 'first_name', 'email', 'is_active')
    exclude = ('last_login', 'groups', 'user_permissions', 'date_joined')
