from django.urls import path
from . import views


app_name = 'orders'


urlpatterns = [
    path('cart/', views.CartView.as_view(), name='view_cart'),
    path('addcart/<int:product_id>/', views.CartAddView.as_view(), name='add_to_cart'),
    path('removecart/<int:product_id>/', views.CartRemoveView.as_view(), name='remove_from_cart'),
    path('create_order/', views.OrderCreateView.as_view(), name='order_create'),
    path('orders_view/', views.OrdersUserView.as_view(), name='orders_view'),
    path('order_detail/<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('apply_discount/<int:order_id>/', views.OrderApplyDiscount.as_view(), name='apply_discount'),
    path('remove_discount/<int:order_id>/', views.OrderRemoveDiscount.as_view(), name='remove_discount'),
    path('pay/<int:order_id>/', views.OrderPayView.as_view(), name='order_pay'),
    path('verify_pay/', views.OrderVerifyView.as_view(), name='order_verify'),
    path('tracking_order/', views.TrackingOrderView.as_view(), name='tracking_order'),
]
