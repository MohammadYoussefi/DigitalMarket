from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User


class Brand(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=40)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField()
    release_date = models.DateField()
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    condition = models.CharField(
        max_length=10,
        choices=[('new', 'نو'), ('used', 'استوک')],
        default='new'
    )
    cleanliness_grade = models.CharField(
        max_length=20,
        choices=[
            ('A0', ' (دستگاه آکبند می باشد)'),
            ('A+', 'A+ (در حد نو)'),
            ('A', 'A (بسیار تمیز)'),
            ('B', 'B (تمیز با خط و خش جزئی)'),
            ('C', 'C (خط و خش مشخص)'),
            ('D', 'D (دارای آسیب‌های ظاهری)')
        ],
        default='A', blank=True, null=True
    )

    def __str__(self):
        return f'{self.name} - {self.brand}'

    @property
    def average_rating(self):
        avg = self.ratings.aggregate(models.Avg('score'))['score__avg']
        return float(avg) if avg is not None else 0.0

    def get_rating_stars(self):
        avg = float(self.average_rating)  # تبدیل به float برای اطمینان
        full_stars = int(avg)
        has_half_star = (avg - full_stars) >= 0.5
        empty_stars = 5 - full_stars - (1 if has_half_star else 0)
        return {
            'full': range(full_stars),
            'half': has_half_star,
            'empty': range(empty_stars),
            'value': avg,
            'count': self.ratings.count()
        }


class ProductSpecs(models.Model):
    laptop = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='product_specs')
    processor_brand = models.CharField(max_length=50)
    processor_model = models.CharField(max_length=100)
    processor_generation = models.CharField(max_length=20, blank=True)
    ram = models.CharField()
    storage = models.CharField(max_length=30)
    gpu_brand = models.CharField(max_length=50)
    gpu_model = models.CharField(max_length=100)
    gpu_memory = models.CharField(max_length=20, blank=True)
    display = models.CharField(max_length=30)
    battery = models.CharField(max_length=50)
    os = models.CharField(max_length=100)
    keyboard_backlight = models.BooleanField(default=False)
    ports = models.TextField(blank=True)
    weight = models.CharField(max_length=20)
    dimensions = models.CharField(max_length=100, blank=True)
    wifi = models.CharField(max_length=50, blank=True)
    bluetooth = models.CharField(max_length=50, blank=True)
    webcam = models.CharField(max_length=50, blank=True)
    speakers = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.laptop.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"تصویر برای {self.product.name}"


class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f'{self.product.name}    |    {self.score}'