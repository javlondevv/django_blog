from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import AbstractUser
from django_resized import ResizedImageField

# Create your models here.
from django.db.models import EmailField, CharField, Model, SlugField, ImageField, ForeignKey, SET_NULL, ManyToManyField, \
    DateField, TextField, SET_DEFAULT, CASCADE, TextChoices, IntegerField, DateTimeField
from django.utils.html import format_html
from django.utils.text import slugify


class User(AbstractUser):
    email = EmailField(max_length=255, unique=True)
    phone = CharField(max_length=255, unique=True)
    image = ImageField(upload_to='%m', null=True, blank=True, max_length=300)

    # bio = TextField(null=True,blank=True)

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Category(Model):
    name = CharField(max_length=255)
    slug = SlugField(max_length=255, unique=True)
    image = ImageField(upload_to='%m', null=True, blank=True)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'

    @property
    def post_count(self):
        return self.post_set.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            while Post.objects.filter(slug=self.slug).exists():
                slug = Post.objects.filter(slug=self.slug).first().slug
                if '-' in slug:
                    try:
                        if slug.split('-')[-1] in self.name:
                            self.slug += '-1'
                        else:
                            self.slug = '-'.join(slug.split('-')[:-1]) + '-' + str(int(slug.split('-')[-1]) + 1)
                    except:
                        self.slug = slug + '-1'
                else:
                    self.slug += '-1'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(Model):
    class Status(TextChoices):
        PENDING = 'pending', 'kutilmoqda'
        ACTIVE = 'active', 'faol'
        CANCEL = 'cancel', 'rad etilgan'

    author = ForeignKey('apps.User', SET_NULL, null=True, blank=True)
    title = CharField(max_length=255, null=True, blank=True)
    category = ManyToManyField(Category, blank=True)
    description = RichTextUploadingField()
    main_picture = ResizedImageField(size=[500, 300], upload_to='%m')
    views = IntegerField(default=0)
    slug = SlugField(max_length=255, unique=True)
    status = CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    created_at = DateTimeField(auto_now_add=True)

    def status_button(self):
        if self.status == Post.Status.PENDING:
            return format_html(
                f'''<a href="active/{self.id}" class="button">Active</a>
                        <a href="cancel/{self.id}" class="button">Cancel</a>'''
            )
        elif self.status == Post.Status.ACTIVE:
            return format_html(
                f'''<a style="color: green; font-size: 1em;margin-top: 8px; margin: auto;">Tasdiqlangan</a>''')

        return format_html(
            f'''<a style="color: red; font-size: 1em;margin-top: 8px; margin: auto;">Tasdiqlanmagan</a>''')

    class Meta:
        verbose_name = "Po'st"
        verbose_name_plural = "Po'stlar"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # if not self.slug:
        self.slug = slugify(self.title)
        while Post.objects.filter(slug=self.slug).exists():
            slug = Post.objects.filter(slug=self.slug).first().slug
            if '-' in slug:
                try:
                    if slug.split('-')[-1] in self.title:
                        self.slug += '-1'
                    else:
                        self.slug = '-'.join(slug.split('-')[:-1]) + '-' + str(int(slug.split('-')[-1]) + 1)
                except:
                    self.slug = slug + '-1'
            else:
                self.slug += '-1'

        super().save(force_insert, force_update, using, update_fields)

    # def __str__(self):
    #     return self.title

    @property
    def comment_count(self):
        return self.comment_set.count()


class Comment(Model):
    comment = TextField()
    author = ForeignKey('apps.User', CASCADE)
    blog = ForeignKey('apps.Post', CASCADE)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kamentariya'
        verbose_name_plural = 'Kamentariyalar'
