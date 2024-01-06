from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)  # A single field for the full name
    # first_name = models.CharField(max_length=30)
    # last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
        # Add related_name attributes to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True,
        verbose_name=_('groups'),
        help_text=_('The groups this user belongs to.'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',
        blank=True,
        verbose_name=_('user permissions'),
        help_text=_('Specific permissions for this user.'),
    )

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

class OrganizerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gdpr_consented = models.BooleanField(default=False, verbose_name="GDPR Consented")
    is_verified = models.BooleanField(default=False, verbose_name="Is Verified")
    # Add other future fields here

    @property
    def is_verified_status(self):
        return self.is_verified

    def __str__(self):
        return self.user.get_full_name()  # Or any other string representation
    
class OrganizerVerificationRequest(models.Model):
    organizer_profile = models.OneToOneField(OrganizerProfile, on_delete=models.CASCADE)
    url = models.URLField()
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Verification request for {self.organizer_profile}"