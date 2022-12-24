from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db.transaction import atomic
from django.forms import ModelForm, PasswordInput, CharField, ModelMultipleChoiceField, CheckboxSelectMultiple
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from apps.models import User, Comment, Category, Post, Message


class RegisterForm(ModelForm):

    def clean(self):
        data = super().clean()
        data['password'] = make_password(data['password'])
        return data

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'phone')


class EditProfile(ModelForm):
    class Meta:
        model = User
        fields = ('image', 'first_name', 'last_name', 'email', 'phone', 'biography')


@atomic
def save(self):
    user = User.objects.create_user(
        username=self.cleaned_data.get('username'),
        email=self.cleaned_data.get('email'),
        phone=self.cleaned_data.get('phone'),
    )
    user.set_password(self.cleaned_data.get('password'))
    user.save()


class LeaveCommentForm(ModelForm):
    class Meta:
        model = Comment
        # fields = ('author', 'comment', 'created_at')
        exclude = ()


class LoginForm(AuthenticationForm):
    def clean_password(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = User.objects.get(username=username)
        if user and not user.check_password(password):
            raise ValidationError('Please check Username or password !')
        return password


class UpdateForm(ModelForm):
    confirm_password = CharField(widget=PasswordInput(attrs={"autocomplete": "current-password"}))
    old_password = CharField(widget=PasswordInput(attrs={"autocomplete": "current-password"}))

    def clean_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if confirm_password != password:
            raise ValidationError('Please,check your password !')
        return make_password(password)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password', 'email', 'phone')


def __init__(self, *args, **kwargs):
    self.fields['password'].required = False
    self.fields['confirm_password'].required = False


class CreateComment(ModelForm):
    class Meta:
        model = Comment
        exclude = ()


class AddPostForm(ModelForm):
    category = ModelMultipleChoiceField(
        queryset=Category.objects.order_by('name'),
        label='Category',
        widget=CheckboxSelectMultiple
    )

    class Meta:
        model = Post
        fields = ('title', 'main_picture', 'category', 'description')


class ChangePasswordForm(ModelForm):
    def clean_password(self):
        user = self.instance
        password = self.data.get('password')
        new_password = self.data.get('new_password')
        confirm_password = self.data.get('confirm_password')
        if new_password == confirm_password:
            if user.check_password(password):
                return make_password(new_password)
            raise ValidationError('Old password isn\'t correct!')
        raise ValidationError('New Password did not match!')

    class Meta:
        model = User
        fields = ('password',)


class MessageForm(ModelForm):
    name = CharField(max_length=255)
    message = CharField()

    class Meta:
        model = Message
        fields = ('name', 'message')
