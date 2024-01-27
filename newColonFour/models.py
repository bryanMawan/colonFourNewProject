from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.postgres.fields import ArrayField  # Only if using PostgreSQL
from .services import generate_unique_slug, default_image, COUNTRY_CHOICES


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
        return f"{self.name}"

    def get_short_name(self):
        return self.name
    

class OrganizerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gdpr_consented = models.BooleanField(default=False, verbose_name="GDPR Consented")
    is_verified = models.BooleanField(default=False, verbose_name="Is Verified")
    slug = models.SlugField(unique=True, blank=True)
    profile_picture = models.ImageField(upload_to='organizer_pics/', null=True, blank=True)
    goings = models.IntegerField(default=0)
    number_of_events = models.IntegerField(default=0)
    organizer_events = models.ManyToManyField('Event', related_name='organizer_profiles')

    def get_profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        else:
            return default_image

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(OrganizerProfile, self.user.get_full_name())
        super(OrganizerProfile, self).save(*args, **kwargs)

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
    

class Event(models.Model):

    organizer = models.ForeignKey(
        'OrganizerProfile',  # Assuming OrganizerProfile is in the same app. If not, use 'app_name.ModelName'
        on_delete=models.CASCADE,  # Defines what happens when the referenced OrganizerProfile is deleted. CASCADE means the event will also be deleted.
        related_name='organized_events',  # Allows access from OrganizerProfile to related events.
        null=True,  # Allows an event to exist without an organizer.
        blank=True,  # Allows the field to be blank in forms and admin.
    )
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    is_hidden = models.BooleanField(default=True)
    number_of_interests = models.IntegerField(default=0)
    number_of_organizer_interests = models.IntegerField(default=0)
    start_time = models.TimeField(null=True, blank=True) #temporal
    end_time = models.TimeField(null=True, blank=True) #temporal
    # level(open, beginner ...)
    styles = ArrayField(models.CharField(max_length=100),null=True, blank=True)
    viewed = models.IntegerField(default=0)
    poster = models.ImageField(upload_to='event_posters/', null=True, blank=True)
    video = models.FileField(upload_to='event_videos/', null=True, blank=True)  # If storing video files
    # video = models.URLField(null=True, blank=True)  # If using video URLs

    # Methods for your specific logic
    def contains_style(self, style):
        # Implementation for checking style
        pass

    def distance_from(self, city):
        # Implementation for calculating distance from a city
        pass 

    def time_in_days_from(self, date):
        # Implementation for calculating time in days from a given date
        pass

    def increment_view_count(self):
        self.viewed += 1
        self.save()

    def __str__(self):
        return self.name


class Dancer(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=3, choices=COUNTRY_CHOICES)  # Use a CharField with choices
    picture = models.ImageField(upload_to='dancer_pics/', null=True, blank=True)
    styles = ArrayField(models.CharField(max_length=100))
    dancer_has_consented = models.BooleanField(default=False)  # Add the new field



    # Many-to-many relationship with Event
    events = models.ManyToManyField('Event', related_name='dancers')

    def get_picture_url(self):
        if self.picture and hasattr(self.picture, 'url'):
            return self.picture.url
        else:
            return default_image

    def __str__(self):
        return self.name 
    
    def get_styles(self):
        return list(self.styles)

class Workshop(Event):
    # Additional fields specific to Workshop can be added here
    # price
    # teacher(s) dancer model
    # guest(s) model
    pass


class Battle(Event):
    # Additional fields specific to Battle can be added here
    pass


class Showcase(Event):
    # Additional fields specific to Showcase can be added here
    pass