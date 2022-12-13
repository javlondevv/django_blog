from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, FormView, CreateView

from apps.forms import RegisterForm, LoginForm, UpdateForm, EditProfile, AddPostForm, ChangePasswordForm, \
    LeaveCommentForm
from apps.models import Post, Category, User, Comment

# Create your views here.
from apps.token import one_time_token


class MainPageView(ListView):
    template_name = 'apps/index.html'
    queryset = Post.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['main_blog'] = Post.objects.last()
        context['blogs'] = Post.objects.order_by('-created_at')[:6]
        context['news'] = Post.objects.order_by('created_at', 'title')[:5]
        context['categories'] = Category.objects.all()
        context['trending'] = Post.objects.order_by('views').all()[:5]

        return context


class BlogListView(ListView):
    template_name = 'apps/blog-category.html'
    paginate_by = 5
    queryset = Post.objects.order_by('created_at', 'title').all()
    context_object_name = 'blogs'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        slug = self.request.GET.get('category')
        context['category'] = Category.objects.filter(slug=slug).first()

        context['news'] = Post.objects.order_by('created_at', 'title')[:5]
        context['trending'] = Post.objects.all()[:5]

        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if category := self.request.GET.get('category'):
            return qs.filter(category__slug=category)
        return qs


class AboutPageView(TemplateView):
    template_name = 'apps/about.html'


class ContactPageView(TemplateView):
    template_name = 'apps/contact.html'


class AddPostView(CreateView):
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
    queryset = Post.objects.all()
    context_object_name = 'post'



class RegisterPageView(FormView):
    form_class = RegisterForm
    success_url = reverse_lazy('login_view')
    template_name = 'auth/auth/signup.html'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})


class LoginPageView(LoginView):
    form_class = LoginForm
    template_name = 'auth/auth/login.html'
    next_page = reverse_lazy('main_page_view')

    # success_url = reverse_lazy('main_page_view')

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
    template_name = 'auth/auth/login.html'
    next_page = reverse_lazy('main_page_view')

    def get_success_url(self):
        return super().get_success_url()


class ProfileSettingView(UpdateView):
    form_class = EditProfile
    model = User
    template_name = 'apps/edit_profile.html'
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
    success_url = reverse_lazy('post_view')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)



class AccountSettingsMixin(View):
    def check_1time_link(self, data):
        uid64 = data.get('uid64')
        token = data.get('token')
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=uid)
        except:
            user = None
        if user is not None and one_time_token.check_token(user, token):
            user.is_active = True
            user.save()
            return user
        return False


class ChangePasswordView(AccountSettingsMixin, UpdateView):
    form_class = ChangePasswordForm
    success_url = reverse_lazy('main_page_view')
    template_name = 'apps/index.html'

    def get_object(self, queryset=None):
        return self.request.user


# class ResetPasswordView(AccountSettingsMixin,UpdateView):


class FooterView(ListView):
    template_name = 'apps/parts/footer.html'
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['footers'] = Post.objects.filter('created_at').all()[:3]
        context['categories'] = Category.objects.all()
        return context


class BLogUpdateView(UpdateView, LoginRequiredMixin):
    model = Post
    fields = ('title', 'description', 'category', 'main_pic')
    success_url = reverse_lazy('main_view')


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UpdateForm
    success_url = reverse_lazy('main_view')
    template_name = 'auth/auth/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        user = User.objects.filter(id=form.id)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


def __repr__(self):
    return "Item"
