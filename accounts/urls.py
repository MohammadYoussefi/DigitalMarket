from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('user_verify/', views.UserVerificationView.as_view(), name='user_verification'),
    path('verify/', views.VerifyOTPView.as_view(), name='verify_otp'),
    path('register/', views.CompleteRegistrationView.as_view(), name='complete_registration'),
    path('restore-password/', views.RestorePassword.as_view(), name='restore_password'),
    path('complete-restore/', views.CompleteRestorePassword.as_view(), name='complete_restore_password'),
    path('change-password/', views.ChangePassword.as_view(), name='change_password'),

]