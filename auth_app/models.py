from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission,
)
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.user_id = str(uuid.uuid4())
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, first_name, last_name, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, first_name, last_name, password, **extra_fields)

#User Model
class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="auth_app_user_set", blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name="auth_app_user_set", blank=True
    )

    objects = UserManager()

    #This ensures the email address is taken as the first_name so user authentication works out well.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

#Organisation Model
class Organisation(models.Model):
    org_id = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, related_name="organisations")

    def __str__(self):
        return self.name
