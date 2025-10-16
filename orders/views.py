from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import AddOrderForm, DiscountCodeForm
from products.models import Product
from .models import DiscountCode, Order, OrderItem
from .cart import CartOrder
from django.contrib import messages
from django.conf import settings
import requests
import json
import utils
from django.http import HttpResponse, HttpResponseRedirect


class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart = CartOrder(request)
        return render(request, 'orders/cart.html', {'cart': cart})


class CartAddView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        cart = CartOrder(request)
        product = Product.objects.get(id=product_id)
        form = AddOrderForm(request.POST)
        if product and product.available is True:
            if form.is_valid():
                cart.add(product, form.cleaned_data['quantity'])
                messages.success(request, 'محصول با موفقیت به سبد خرید شما اضافه شد')
        return redirect('orders:view_cart')


class CartRemoveView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        cart = CartOrder(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove_product(product)
        messages.success(request, 'محصول با موفقیت از سبد خرید شما حذف شد')
        return redirect('orders:view_cart')


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = CartOrder(request)
        order = Order.objects.create(user=request.user)
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
        cart.clear_cart()
        return redirect('orders:order_detail', order.id)


class OrdersUserView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        return render(request,'orders/orders_view.html' ,{'orders': orders})


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        form = DiscountCodeForm()
        return render(request, 'orders/view_order.html', {'order': order, 'discount_form': form})


class OrderApplyDiscount(LoginRequiredMixin, View):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        form = DiscountCodeForm(request.POST)

        if not form.is_valid():
            messages.error(request, "فرمت کد تخفیف اشتباه می باشد!")
            return redirect('orders:order_detail', order.id)

        cd = form.cleaned_data
        try:
            discount_code = DiscountCode.objects.get(code=cd['code'])
        except DiscountCode.DoesNotExist:
            messages.error(request, "کد تخفیف نامعتبر است!")
            return redirect('orders:order_detail', order.id)

        if not discount_code.is_valid():
            messages.error(request, "مهلت یا ظرفیت استفاده از این کد تخفیف تمام شده است!")
            return redirect('orders:order_detail', order.id)

        if order.discount and order.discount.code == cd['code']:
            messages.success(request, 'این کد تخفیف در حال حاضر اعمال شده است')
            return redirect('orders:order_detail', order.id)

        if order.discount and order.discount.code != cd['code']:
            order.discount.remove_use_code()

        order.discount = discount_code
        discount_code.use_code()
        order.save()

        messages.success(request, 'کد تخفیف با موفقیت اعمال شد')
        return redirect('orders:order_detail', order.id)


class OrderRemoveDiscount(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = Order.objects.get(id=order_id)
        if order.discount:
            order.discount.remove_use_code()
            order.discount = None
            order.save()
            messages.success(request, 'کد تخفیف با موفقیت حذف شد')
        else:
            messages.error(request, '!کد تخفیفی برای حذف وجود ندارد')
        return redirect('orders:order_detail', order_id)


# Sandbox or production
if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
CallbackURL = 'http://127.0.0.1:8080/orders/verify_pay/'


class OrderPayView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = Order.objects.get(id=order_id)

        request.session['order_pay'] = {
            'order_id': order.id
        }

        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": order.get_price_after_discount(),
            "Description": f"پرداخت سفارش {order.id}",
            "Phone": request.user.phone_number,
            "CallbackURL": CallbackURL,
        }

        json_data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(json_data))}

        try:
            response = requests.post(ZP_API_REQUEST, data=json_data, headers=headers, timeout=10)
            if response.status_code == 200:
                response_data = response.json()
                if response_data['Status'] == 100:
                    authority = response_data['Authority']
                    return HttpResponseRedirect(ZP_API_STARTPAY + authority)
                else:
                    return render(request, "orders/payment_failed.html", {
                        "message": f"خطا در درخواست پرداخت. کد وضعیت: {response_data['Status']}"
                    })
            else:
                return render(request, "orders/payment_failed.html", {
                    "message": "خطا در ارتباط با سرور زرین‌پال."
                })

        except requests.exceptions.Timeout:
            return render(request, "orders/payment_failed.html", {
                "message": "Timeout هنگام ارتباط با زرین‌پال."
            })
        except requests.exceptions.ConnectionError:
            return render(request, "orders/payment_failed.html", {
                "message": "خطای ارتباط با سرور زرین‌پال."
            })


class OrderVerifyView(LoginRequiredMixin, View):
    def get(self, request):
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')

        if status != 'OK':
            return render(request, "orders/payment_failed.html", {
                "message": "پرداخت توسط کاربر لغو شد."
            })

        order_id = request.session['order_pay']['order_id']
        order = Order.objects.get(id=int(order_id))

        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": order.get_price_after_discount(),
            "Authority": authority,
        }

        json_data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(json_data))}

        try:
            response = requests.post(ZP_API_VERIFY, data=json_data, headers=headers, timeout=10)
            if response.status_code == 200:
                response_data = response.json()
                print("Zarinpal Verify Response:", response_data)
                if response_data['Status'] == 100:
                    order.paid = True
                    order.save()
                    tracking_code = order.generate_tracking_code()
                    utils.send_tracking_code(request.user.phone_number, tracking_code)
                    return render(request, "orders/payment_success.html", {
                        "order": order,
                        "ref_id": response_data['RefID'],
                        "tracking_code": tracking_code,
                    })
                else:
                    return render(request, "orders/payment_failed.html", {
                        "message": f"پرداخت تایید نشد. کد وضعیت: {response_data['Status']}"
                    })
            else:
                return render(request, "orders/payment_failed.html", {
                    "message": "خطا در تایید پرداخت با زرین‌پال."
                })

        except requests.exceptions.Timeout:
            return render(request, "orders/payment_failed.html", {
                "message": "Timeout در هنگام تایید پرداخت."
            })
        except requests.exceptions.ConnectionError:
            return render(request, "orders/payment_failed.html", {
                "message": "خطای ارتباط با سرور زرین‌پال."
            })


class TrackingOrderView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'orders/tracking_order.html')

    def post(self, request):
        tracking_code = request.POST.get('tracking_code')

        if not tracking_code:
            return render(request, 'orders/tracking_order.html', {
                'error': "لطفاً کد پیگیری را وارد کنید."
            })

        order = Order.objects.filter(tracking_id=tracking_code).first()

        if not order:
            return render(request, 'orders/tracking_order.html', {
                'error': "کد پیگیری وارد شده یافت نشد!"
            })

        return render(request, 'orders/tracking_order.html', {
            'order': order,
            'tracking': order,
        })

