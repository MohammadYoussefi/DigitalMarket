from django.db import models
from accounts.models import User
from products.models import Product
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField


class BlogPost(models.Model):
    STATUS_CHOICES = (
        ('draft', 'پیش‌نویس'),
        ('published', 'منتشر شده'),
    )

    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='اسلاگ')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name='نویسنده')
    content = RichTextField(verbose_name='محتوا')
    summary = models.TextField(max_length=500, verbose_name='خلاصه مطلب')
    image = models.ImageField(upload_to='blog/images/', verbose_name='تصویر اصلی')

    related_products = models.ManyToManyField(Product, blank=True, verbose_name='لپتاپ‌های مرتبط')

    publish_date = models.DateTimeField(default=timezone.now, verbose_name='تاریخ انتشار')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='وضعیت')
    view_count = models.IntegerField(blank=True, default=0, verbose_name='تعداد بازدید')

    meta_title = models.CharField(max_length=60, blank=True, verbose_name='عنوان متا')
    meta_description = models.CharField(max_length=160, blank=True, verbose_name='توضیحات متا')

    class Meta:
        ordering = ('-publish_date',)
        verbose_name = 'پست وبلاگ'
        verbose_name_plural = 'پست‌های وبلاگ'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('webl', args=[self.slug])