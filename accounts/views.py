from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
import utils
from .forms import UserLoginForm, UserRegistrationForm, UserVerificationForm, RestorePasswordForm, ChangePasswordForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User, OTPCode
import random
from django.contrib.auth.mixins import LoginRequiredMixin


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/user_login.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'login_form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = None
            try:
                user = User.objects.get(phone_number=cd['email_or_phone'])
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=cd['email_or_phone'])
                except User.DoesNotExist:
                    user = None

            if user:
                user = authenticate(request, email=user.email, password=cd['password'])
                if user is not None:
                    login(request, user)
                    messages.success(request, 'با موفقیت وارد شدید')
                    return redirect('home:home')
                else:
                    messages.error(request, 'رمز عبور اشتباه است!')
            else:
                messages.error(request, 'کاربر یافت نشد! لطفاً شماره تلفن یا ایمیل را صحیح وارد کنید.')
        return render(request, self.template_name, {'login_form': form})


class UserLogoutView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'ابتدا به حساب کاربری خود وارد شوید')
            return redirect('accounts:user_login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        logout(request)
        messages.success(request, 'با موفقیت از حساب کاربری خارج شدید')
        return redirect('home:home')


class UserVerificationView(View):
    form_class = UserVerificationForm

    def get(self, request):
        form = self.form_class()
        return render(request, 'accounts/user_verification.html', {'user_verify_form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            if User.objects.filter(phone_number='phone_number').exists():
                messages.error(request, 'این شماره تلفن قبلاً ثبت‌نام شده است')
                return redirect('accounts:user_verification')

            code = random.randint(10000, 99999)
            OTPCode.objects.create(phone_number=phone_number, code=code)
            utils.send_otp_code(phone_number, code)
            request.session['phone_number'] = phone_number
            request.session['registration_in_progress'] = True
            messages.success(request, 'کد یکبار مصرف با موفقیت ارسال شد')
            return redirect('accounts:verify_otp')

        messages.error(request, 'شماره تلفن معتبر نیست')
        return redirect('accounts:user_verification')


class VerifyOTPView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('registration_in_progress'):
            return redirect('accounts:user_verification')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'accounts/enter_otp.html')

    def post(self, request):
        if not request.session.get('registration_in_progress'):
            return redirect('accounts:user_verification')

        otp_code_input = request.POST.get('otp_code')
        phone_number = request.session.get('phone_number')

        try:

            otp = OTPCode.objects.filter(phone_number=phone_number, code=otp_code_input).first()
            if not otp:
                messages.error(request, 'کد وارد شده صحیح نیست یا منقضی شده است')
                return redirect('accounts:verify_otp')

            if otp.is_expired():
                messages.error(request, 'کد وارد شده منقضی شده است. لطفاً دوباره تلاش کنید.')
                otp.delete()
                return redirect('accounts:user_verification')

            OTPCode.objects.filter(phone_number=phone_number).delete()
            request.session['otp_verified'] = True
            return redirect('accounts:complete_registration')

        except OTPCode.DoesNotExist:
            messages.error(request, 'کد وارد شده صحیح نیست')
            return redirect('accounts:verify_otp')


class CompleteRegistrationView(View):
    form_class = UserRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('registration_in_progress'):
            return redirect('accounts:verify_otp')
        if not request.session.get('otp_verified'):
            return redirect('accounts:verify_otp')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        phone_number = request.session.get('phone_number')
        form = self.form_class(initial={'phone_number': phone_number})
        return render(request, 'accounts/final_registration.html', {'register_form': form})

    def post(self, request):
        if not request.session.get('registration_in_progress'):
            return redirect('accounts:verify_otp')
        if not request.session.get('otp_verified'):
            return redirect('accounts:verify_otp')

        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    email=form.cleaned_data['email'],
                    phone_number=request.session['phone_number'],
                    full_name=form.cleaned_data['full_name'],
                    password=form.cleaned_data['password1'],
                )
                del request.session['phone_number']
                del request.session['registration_in_progress']
                del request.session['otp_verified']
                messages.success(request, 'ثبت‌نام شما با موفقیت انجام شد')
                login(request, user)
                return redirect('home:home')
            except Exception as e:
                messages.error(request, 'خطایی در ثبت اطلاعات رخ داد')
                return redirect('accounts:complete_registration')

        messages.error(request, 'لطفاً اطلاعات را به درستی وارد کنید')
        return render(request, 'accounts/final_registration.html', {'register_form': form})


class RestorePassword(View):
    def get(self, request):
        form = RestorePasswordForm()
        return render(request, 'accounts/restore_password.html', {'form': form})

    def post(self, request):
        phone_number = request.POST.get('phone_number')

        if not User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'کاربری با این شماره وجود ندارد')
            return redirect('accounts:restore_password')

        OTPCode.objects.filter(phone_number=phone_number).delete()

        code = str(random.randint(10000, 99999))
        otp = OTPCode.objects.create(phone_number=phone_number, code=code)

        request.session['phone_number_restore'] = phone_number

        utils.send_otp_code_for_password(phone_number, code)
        messages.success(request, 'کد تغییر پسورد ارسال شد')
        return redirect('accounts:complete_restore_password')


class CompleteRestorePassword(View):
    def get(self, request):
        form = ChangePasswordForm()
        return render(request, 'accounts/complete_restore.html', {'form': form})

    def post(self, request):
        phone_number = request.session.get('phone_number_restore')
        code = request.POST.get('code')

        if not phone_number:
            messages.error(request, 'دوباره تلاش کنید')
            return redirect('accounts:restore_password')

        otp = OTPCode.objects.filter(phone_number=phone_number).last()

        if not otp:
            messages.error(request, 'کدی یافت نشد، دوباره درخواست کنید')
            return redirect('accounts:restore_password')

        if otp.is_expired():
            otp.delete()
            messages.error(request, 'کد منقضی شده است')
            return redirect('accounts:restore_password')

        if otp.code == code:
            otp.delete()
            messages.success(request, 'اعتبارسنجی موفق بود')
            request.session['otp_verified'] = True
            return redirect('accounts:change_password')
        else:
            messages.error(request, 'کد وارد شده معتبر نیست')
            return redirect('accounts:complete_restore_password')


class ChangePassword(View):
    def get(self, request):
        if not request.session.get('otp_verified'):
            messages.error(request, 'ابتدا باید کد تایید را وارد کنید')
            return redirect('accounts:restore_password')

        form = ChangePasswordForm()
        return render(request, 'accounts/change_password.html', {'form': form})

    def post(self, request):
        if not request.session.get('otp_verified'):
            messages.error(request, 'ابتدا باید کد تایید را وارد کنید')
            return redirect('accounts:restore_password')

        phone_number = request.session.get('phone_number_restore')
        form = ChangePasswordForm(request.POST)

        if form.is_valid():
            user = User.objects.get(phone_number=phone_number)
            user.set_password(form.cleaned_data['password'])
            user.save()

            request.session.pop('phone_number_restore', None)
            request.session.pop('otp_verified', None)

            messages.success(request, 'رمز عبور با موفقیت تغییر کرد')
            return redirect('accounts:user_login')
        else:
            messages.error(request, 'خطا در تغییر رمز عبور')
            return render(request, 'accounts/change_password.html', {'form': form})
