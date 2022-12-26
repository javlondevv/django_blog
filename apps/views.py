import os
from datetime import datetime

import qrcode
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, FormView, CreateView

from apps.forms import RegisterForm, LoginForm, UpdateForm, EditProfile, AddPostForm, ChangePasswordForm, \
    LeaveCommentForm, MessageForm
from apps.models import Post, Category, User, Comment, PostViewHistory

# Create your views here.
from apps.utils import render_to_pdf, send_to_gmail, send_to_contact, one_time_token


class AccountSettingMixin(View):
    def check_one_time_link(self, data):
        uid64 = data.get('uid64')
        token = data.get('token')
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=uid)
        except Exception as e:
            print(e)
            user = None
        if user and one_time_token.check_token(user, token):
            user.is_active = True
            user.save()
            return user
        return False


class GeneratePdf(DetailView):
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        post = Post.objects.get(slug=kwargs.get('slug'))
        url = f'{get_current_site(request)}/post/{post.slug}'

        img = qrcode.make(url)
        img.save(post.slug + '.png')

        data = {
            'post': post,
            'qrcode': f'{os.getcwd()}/{post.slug}.png'
        }
        print(os.getcwd())
        pdf = render_to_pdf('pdf.html', data)
        os.remove(f'{post.slug}.png')
        return HttpResponse(pdf, content_type='application/pdf')


class MainPageView(ListView):
    template_name = 'apps/index.html'
    queryset = Post.active.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['main_blog'] = Post.active.last()
        context['blogs'] = Post.active.order_by('-created_at')[:6]
        context['news'] = Post.active.order_by('created_at', 'title')[:5]
        context['categories'] = Category.objects.all()
        context['trending'] = Post.active.order_by('postviewhistory').all()[:5]

        return context


class BlogListView(ListView):
    template_name = 'apps/blog-category.html'
    paginate_by = 5
    queryset = Post.active.order_by('created_at', 'title').all()
    context_object_name = 'blogs'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        slug = self.request.GET.get('category')
        context['category'] = Category.objects.filter(slug=slug).first()

        context['news'] = Post.active.order_by('created_at', 'title')[:5]
        context['trending'] = Post.active.order_by('postviewhistory').all()[:5]

        return context

    def post(self, request, *args, **kwargs):
        post = request.POST.get('post')
        comment = request.POST.get('comment')
        author = request.user
        obj = Comment.objects.create(comment=comment, blog_id=post, author=author)
        return redirect(reverse('post_view', kwargs={'slug': obj.blog.slug}))

    def get_queryset(self):
        qs = super().get_queryset()
        if category := self.request.GET.get('category'):
            return qs.filter(category__slug=category)
        return qs


class AboutPageView(TemplateView):
    template_name = 'apps/about.html'


class ContactPageView(FormView):
    template_name = 'apps/contact.html'
    form_class = MessageForm
    success_url = reverse_lazy('main_page_view')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)


class AddPostView(LoginRequiredMixin, CreateView):
    template_name = 'apps/add-post.html'
    form_class = AddPostForm
    success_url = reverse_lazy('main_page_view')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})


class BlogPageView(DetailView):
    template_name = 'apps/post.html'
    query_pk_and_slug = 'slug'
    queryset = Post.active.all()
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['views'] = PostViewHistory.objects.all()
        return context


class RegisterPageView(FormView):
    form_class = RegisterForm
    success_url = reverse_lazy('login_view')
    template_name = 'apps/auth/signup.html'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})


class LoginPageView(LoginView):
    form_class = LoginForm
    template_name = 'apps/auth/login.html'
    next_page = reverse_lazy('main_page_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forms'] = LoginForm
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    form_class = LoginForm()
    template_name = 'apps/auth/login.html'
    next_page = reverse_lazy('main_page_view')

    def get_success_url(self):
        return super().get_success_url()


class ProfileSettingView(UpdateView):
    form_class = EditProfile
    model = User
    template_name = 'apps/auth/edit_profile.html'
    success_url = reverse_lazy('edit_profile_view')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class LeaveCommentView(FormView):
    form_class = LeaveCommentForm
    model = Comment
    success_url = reverse_lazy("post_view")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ChangePasswordView(AccountSettingMixin, UpdateView):
    form_class = ChangePasswordForm
    success_url = reverse_lazy('edit_profile_view')
    template_name = 'apps/auth/change_password.html'

    def form_valid(self, form):
        username = self.request.user.username
        valid_form = super().form_valid(form)
        password = form.data.get('new_password')
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
        return valid_form

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_object(self, queryset=None):
        return self.request.user


class ResetPasswordView(AccountSettingMixin, UpdateView):
    template_name = 'apps/auth/reset_password.html'
    success_url = reverse_lazy('main_page_view')

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        if 'save_password' in request.POST:
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            error = ''
            if password != confirm_password:
                error = 'Password did not match!'
            try:
                pk = force_str(urlsafe_base64_decode(request.POST.get('user')))
                user = User.objects.get(pk=pk)
            except:
                user = None
            if not user:
                error = 'User is not found on this server'
            if error:
                return render(request, self.template_name, {'type': 'expired', 'error': error})
            user.set_password(password)
            user.save()
            return redirect('login_view')

        email = self.request.POST.get('email')
        current_site = get_current_site(self.request)
        if user := User.objects.get(email=email):
            user.is_active = False
            user.save()
            send_to_gmail.apply_async(
                args=[email, current_site.domain, 'reset'],
                countdown=5
            )
            return render(request, self.template_name, {'type': 'valid'})
        return super().post(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.GET.get('uid64') and request.GET.get('token'):
            if user := self.check_one_time_link(request.GET):
                return render(request, self.template_name,
                              {'reset_password_user': urlsafe_base64_encode(force_bytes(str(user.pk)))})
            return render(request, self.template_name,
                          {'type': 'expired', 'error': 'Your link has been already expired !'})
        return render(request, self.template_name)


class BLogUpdateView(UpdateView, LoginRequiredMixin):
    model = Post
    fields = ('title', 'description', 'category', 'main_pic')
    success_url = reverse_lazy('main_page_view')


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UpdateForm
    success_url = reverse_lazy('main_view')
    template_name = 'apps/auth/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def __repr__(self):
        return "Item"
