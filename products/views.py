from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from products.models import Product, Brand, Rating
from orders.forms import AddOrderForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class ProductListView(View):
    def get(self, request, brand_slug=None):
        products = Product.objects.all()
        brands = Brand.objects.prefetch_related('products')
        form = AddOrderForm
        if brand_slug:
            selected_brand = get_object_or_404(Brand, slug=brand_slug)
            products = products.filter(brand=selected_brand)
        return render(request, 'products/products.html', {'products': products,
                                                          'add_cart_form': form,
                                                          'brands': brands})


class ProductDetailView(View):
    def get(self, request, product_id):
        product = Product.objects.get(id=product_id)
        return render(request, 'products/product_detail.html', {'product': product})


class RateProductView(View, LoginRequiredMixin):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        if request.method == 'POST':
            rating = int(request.POST.get('rating', 0))

            if 1 <= rating <= 5:
                Rating.objects.update_or_create(
                    product=product,
                    user=request.user,
                    defaults={'score': rating}
                )
                messages.success(request, 'امتیاز شما با موفقیت ثبت شد.')
            else:
                messages.error(request, 'امتیاز نامعتبر است.')

        return redirect('products:product_detail', product_id=product.id)