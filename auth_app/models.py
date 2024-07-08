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

    def create_user(
        self, email, firstName, lastName, phone=None, password=None, **extra_fields
    ):
        if not email:
            raise ValueError("The Email field must be set")
        if not firstName:
            raise ValueError("The First Name field must be set")
        if not lastName:
            raise ValueError("The Last Name field must be set")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            firstName=firstName,
            lastName=lastName,
            phone=phone,
            **extra_fields
        )
        user.userId = str(uuid.uuid4())
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, firstName, lastName, phone=None, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(
            email, firstName, lastName, phone, password, **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    userId = models.CharField(max_length=255, unique=True)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["firstName", "lastName"]

    def __str__(self):
        return self.email


class Organisation(models.Model):
    orgId = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, related_name="organisations")

    def __str__(self):
        return self.name
