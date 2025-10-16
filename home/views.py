from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from products.models import Product, Brand
from django.db.models import Q


class HomeView(View):
    def get(self, request, brand_slug=None):
        brands = Brand.objects.all()
        products = Product.objects.all()

        if brand_slug:
            selected_brand = get_object_or_404(Brand, slug=brand_slug)
            products = products.filter(brand=selected_brand)

        return render(request, 'home/home.html', {
            'products': products,
            'brands': brands,
            'selected_brand_slug': brand_slug
        })


class SearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        products = Product.objects.none()
        if query:
            products = Product.objects.filter(
                Q(name__icontains=query) | Q(brand__name__icontains=query)
            )
        return render(request, 'home/search_results.html', {
            'products': products,
            'query': query
        })


class ContactView(View):
    def get(self, request):
        return render(request, 'home/contact_us.html')