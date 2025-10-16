from django.contrib import admin
from .models import Product, Brand, ProductSpecs, ProductImage, Rating


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text']
    readonly_fields = []


class ProductSpecsInline(admin.StackedInline):
    model = ProductSpecs
    can_delete = False
    verbose_name_plural = 'مشخصات فنی'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'price', 'condition']
    search_fields = ['name', 'brand__name']
    list_filter = ['brand', 'condition', 'cleanliness_grade']
    inlines = [ProductSpecsInline, ProductImageInline]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'alt_text']
    search_fields = ['product__name']


admin.site.register(Rating)