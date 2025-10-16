from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, full_name, password=None):
        if not email:
            raise ValueError('ایمیل باید وارد شود')
        if not full_name:
            raise ValueError('نام کامل باید وارد شود')
        if not phone_number:
            raise ValueError('شماره تلفن باید وارد شود')
        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            phone_number=phone_number,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, full_name, password=None):
        user = self.create_user(
            email=email,
            phone_number=phone_number,
            full_name=full_name,
            password=password
        )
        user.is_superuser = True
        user.is_admin = True
        user.save(using=self._db)
        return user
