from django.urls import path, include

from apps.views import BlogListView, AboutPageView, ContactPageView, BlogPageView, UserUpdateView, RegisterPageView, \
    LoginPageView, CustomLogoutView, MainPageView, ProfileSettingView, AddPostView, GeneratePdf, ChangePasswordView, \
    ResetPasswordView

urlpatterns = [
    path('', MainPageView.as_view(), name='main_page_view'),
    path('pdf/<str:slug>', GeneratePdf.as_view(), name='make_pdf'),
    path('blog-category/', BlogListView.as_view(), name='blog_category_view'),
    path('about', AboutPageView.as_view(), name='about_view'),
    path('contact', ContactPageView.as_view(), name='contact_view'),
    path('blog/<str:slug>', BlogPageView.as_view(), name='post_view'),

    path('change-password', ChangePasswordView.as_view(), name='change_password'),
    path('reset-password', ResetPasswordView.as_view(), name='reset_password'),

    path('user-edit/<int:pk>', UserUpdateView.as_view(), name='user_update_view'),
    path('register/', RegisterPageView.as_view(), name='register_view'),
    path('login', LoginPageView.as_view(), name='login_view'),
    path('logout', CustomLogoutView.as_view(), name='logout_view'),
    path('edit-profile/', ProfileSettingView.as_view(), name='edit_profile_view'),
    path('add-post/', AddPostView.as_view(), name='add_post_view'),

    path('oauth/', include('social_django.urls', namespace='social')),
]
