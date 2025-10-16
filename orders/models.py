import random

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from products.models import Product
from accounts.models import User


class DiscountCode(models.Model):
    PERCENTAGE = 'percentage'
    FIXED_AMOUNT = 'fixed'
    DISCOUNT_TYPES = [
        (PERCENTAGE, 'درصدی'),
        (FIXED_AMOUNT, 'مقدار ثابت'),
    ]

    code = models.CharField(max_length=20, unique=True, verbose_name='کد تخفیف')
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default=PERCENTAGE,
                                     verbose_name='نوع تخفیف')
    discount_value = models.PositiveIntegerField(verbose_name='مقدار تخفیف',
                                                 validators=[MinValueValidator(1), MaxValueValidator(100)
                                                 if discount_type == PERCENTAGE else MaxValueValidator(100000000)])
    start_date = models.DateTimeField(verbose_name='تاریخ شروع')
    end_date = models.DateTimeField(verbose_name='تاریخ انقضا')
    max_usage = models.PositiveIntegerField(verbose_name='حداکثر تعداد استفاده', default=1)
    current_usage = models.PositiveIntegerField(verbose_name='تعداد استفاده شده', default=0)
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کدهای تخفیف'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()} ({self.discount_value})"

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('تاریخ شروع باید قبل از تاریخ انقضا باشد.')

        if self.discount_type == self.PERCENTAGE and self.discount_value > 100:
            raise ValidationError('تخفیف درصدی نمی‌تواند بیشتر از ۱۰۰٪ باشد.')

    def is_valid(self):
        now = timezone.now()
        return (
                self.is_active and
                self.start_date <= now <= self.end_date and
                (self.max_usage is None or self.current_usage < self.max_usage)
        )

    def use_code(self):
        if self.current_usage < self.max_usage:
            self.current_usage += 1
            self.save()
            return True
        return False

    def remove_use_code(self):
        self.current_usage -= 1
        self.save()
        return True


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discount = models.ForeignKey(DiscountCode, blank=True, null=True, on_delete=models.SET_NULL)
    tracking_id = models.CharField(max_length=5, blank=True, null=True, unique=True)
    tracking_post_code = models.CharField(max_length=30, unique=True, blank=True, null=True)
    delivery = models.BooleanField(default=False)

    class Meta:
        ordering = ('user', 'created_at')

    def __str__(self):
        return f'{self.user} | {self.created_at.date()} | paid: {self.paid}'

    def get_price_after_discount(self):
        total = sum(item.get_cost() for item in self.order_items.all())
        if hasattr(self, 'discount') and self.discount is not None:
            if self.discount.discount_type == 'percentage':
                discount_amount = total * (self.discount.discount_value / 100)
                return int(total - discount_amount)
            else:
                return max(0, int(total - self.discount.discount_value))
        return total

    def get_discount_value(self):
        total = sum(item.get_cost() for item in self.order_items.all())
        return (total / 100) * self.discount.discount_value

    def generate_tracking_code(self):
        """
        ساخت کد پیگیری یکتا (۵ رقمی)
        """
        if not self.paid:
            return "سفارش هنوز پرداخت نشده است"

        if not self.tracking_id:
            while True:
                code = str(random.randint(10000, 99999))
                if not Order.objects.filter(tracking_id=code).exists():
                    self.tracking_id = code
                    self.save(update_fields=["tracking_id"])
                    break
        return f"کد پیگیری سفارش شما: {self.tracking_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.id}'

    def get_cost(self):
        return self.quantity * self.price


