from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User
from django.core.exceptions import ValidationError
import re

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ['phone_number', 'email', 'full_name', 'password1', 'password2']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise ValidationError('پسورد یکسان نیستند')
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password2'])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text='پسورد را تغییر دهید از طریق'
                                                   ' <a href=\"../password/\">این فرم</a>')

    class Meta:
        model = User
        fields = ('phone_number', 'email', 'full_name', 'password', 'last_login')


class UserLoginForm(forms.Form):
    email_or_phone = forms.CharField(
        label="ایمیل یا شماره تلفن",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 pr-12 bg-gray-50 border-2 border-gray-200 rounded-xl '
                     'text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 '
                     'focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200 '
                     'hover:border-emerald-300',
            'placeholder': 'ایمیل یا شماره تلفن',
        }),
        label_suffix='',
    )

    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 pr-12 bg-gray-50 border-2 border-gray-200 rounded-xl '
                     'text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 '
                     'focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200 '
                     'hover:border-emerald-300',
            'placeholder': 'رمز عبور',
        }),
        label_suffix='',
    )


class UserVerificationForm(forms.Form):
    phone_number = forms.CharField()

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        check_phone_number = User.objects.filter(phone_number=phone_number).exists()
        if check_phone_number:
            raise forms.ValidationError('این شماره قبلا ثبت نام شده است')
        return phone_number


class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        label='نام کامل',
        widget=forms.TextInput(attrs={'placeholder': 'نام و نام خانوادگی'})
    )
    password1 = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={'placeholder': 'حداقل ۸ کاراکتر'}))
    password2 = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور'}))

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("پسورد ها همخوانی ندارند")

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        check_email = User.objects.filter(email=email).exists()
        if check_email:
            raise forms.ValidationError('این ایمیل قبلا ثبت نام شده است')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        check_phone_number = User.objects.filter(phone_number=phone_number).exists()
        if check_phone_number:
            raise forms.ValidationError('این شماره قبلا ثبت نام شده است')
        return phone_number


class RestorePasswordForm(forms.Form):
    phone_number = forms.CharField(
        label="شماره موبایل",
        max_length=11,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none block w-full px-4 py-3 rounded-xl border border-gray-300 placeholder-gray-400 "
                         "focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 sm:text-sm "
                         "text-right",
                "placeholder": "مثلاً 09123456789",
                "dir": "ltr",
            }
        )
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']

        if not re.match(r'^\d{11}$', phone_number):
            raise ValidationError('شماره تلفن معتبر نیست')

        if not User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('هیچ کاربری با این شماره ثبت نام نشده است')

        return phone_number


class ChangePasswordForm(forms.Form):
    password = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none block w-full px-4 py-3 rounded-xl border border-gray-300 "
                         "placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 "
                         "focus:border-emerald-400 sm:text-sm text-right",
                "placeholder": "رمز عبور جدید",
            }
        )
    )

    confirm_password = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none block w-full px-4 py-3 rounded-xl border border-gray-300 "
                         "placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 "
                         "focus:border-emerald-400 sm:text-sm text-right",
                "placeholder": "تکرار رمز عبور",
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("پسورد ها همخوانی ندارند")

        return cleaned_data
