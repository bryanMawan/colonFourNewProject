from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.timezone import make_aware, datetime
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.postgres.fields import ArrayField  # Only if using PostgreSQL
from .servicesFolder.services import generate_unique_slug, default_image, COUNTRY_CHOICES, BATTLE_TYPE_CHOICES, LEVEL_CHOICES, distance_between_cities
import logging

logger = logging.getLogger(__name__)


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
    name = models.CharField(max_length=100) 
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
    WORKSHOP = 'workshop'
    BATTLE = 'battle'
    SHOWCASE = 'showcase'
    EVENT_TYPE_CHOICES = [
        (WORKSHOP, 'Workshop'),
        (BATTLE, 'Battle'),
        (SHOWCASE, 'Showcase'),
    ]
    organizer = models.ForeignKey(
        'OrganizerProfile',  # Assuming OrganizerProfile is in the same app. If not, use 'app_name.ModelName'
        on_delete=models.CASCADE,  # Defines what happens when the referenced OrganizerProfile is deleted. CASCADE means the event will also be deleted.
        related_name='organized_events',  # Allows access from OrganizerProfile to related events.
    )
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES, default=WORKSHOP)
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    location_point = models.CharField(max_length=30, blank=True, null=True)
    goers = ArrayField(models.CharField(max_length=64), null=True, blank=True, default=list)
    description = models.TextField()
    is_hidden = models.BooleanField(default=True)
    goings = models.IntegerField(default=0)
    number_of_goings = models.IntegerField(default=0)
    start_time = models.TimeField(null=True, blank=True) #temporal
    end_time = models.TimeField(null=True, blank=True) #temporal
    level = models.CharField(max_length=13, choices=LEVEL_CHOICES, default='1vs1')
    styles = ArrayField(models.CharField(max_length=100),null=True, blank=True)
    viewed = models.IntegerField(default=0)
    poster = models.ImageField(upload_to='colonfourMedia/', null=True, blank=True)
    video = models.FileField(upload_to='event_videos/', null=True, blank=True)  # If storing video files
    # video = models.URLField(null=True, blank=True)  # If using video URLs

    # Methods for your specific logic
    def contains_style(self, style):
        # Implementation for checking style
        pass

    def get_trimmed_location(self):
        # Assuming the format is always "street, city, country"
        parts = self.location.split(", ")
        if len(parts) >= 3:
            return f"{parts[-2]}, {parts[-1]}"
        return self.location  # Fallback to the full location if the format is unexpected
    
    def distance_from(self, target_city):
        
        event_city = self.location.split(',')[1].strip()  # Adjust based on your actual location format
        # Ensure city names are properly capitalized as they might be case-sensitive in your database or geocoding service
        event_city_title = event_city.title()
        target_city_title = target_city.title()
        # Calculate the distance using the function from your services module
        distance = distance_between_cities(event_city_title, target_city_title)
        return distance

    def time_in_days_from(self, date):
        # Implementation for calculating time in days from a given date
        pass

    def increment_view_count(self):
        self.viewed += 1
        self.save()

    def __str__(self):
        return self.name
    
    def get_styles(self):
        # Start with the event's own styles, ensuring they're titled
        unique_styles = set(style.title() for style in self.styles) if self.styles else set()
        
        # Add titled styles from all associated dancers
        for dancer in self.dancers.all():
            unique_styles.update([style.title() for style in dancer.special_get_styles()])
            
        return list(unique_styles)
    def days_until(self, aware_date):
        """
        Calculate the difference in days between the event date and the provided aware date string.
        
        :param aware_date_str: An aware date string in the format "YYYY-MM-DD HH:MM:SS.ffffff+ZZ:ZZ"
        :return: The difference in days as an integer.
        """
        delta = self.date - aware_date
        diff = delta.days

        logger.debug(f"for Event: {self.name}")
        logger.debug(f"This is the date difference: {diff}")
        logger.debug(f"This is the start date: {self.start_time}")

        return diff
    
    def add_goer(self, goer_hash):
        """
        Adds a goer's hash to the goers array if not already present.
        Returns True if the hash was added, False otherwise.
        """
        if goer_hash not in self.goers:
            self.goers.append(goer_hash)
            self.save()
            return True
        return False

    def remove_goer(self, goer_hash):
        """
        Removes a goer's hash from the goers array if present.
        Returns True if the hash was removed, False otherwise.
        """
        if goer_hash in self.goers:
            self.goers.remove(goer_hash)
            self.save()
            return True
        return False
    

    def get_number_of_goers(self):
        """
        Returns the total number of goers' hashes.
        """
        return len(self.goers)


class Dancer(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=3, choices=COUNTRY_CHOICES)  # Use a CharField with choices
    picture = models.ImageField(upload_to='dancer_pics/', null=True, blank=True)
    styles = ArrayField(models.CharField(max_length=100))
    dancer_has_consented = models.BooleanField(default=False)  # Add the new field

    def __str__(self):
        # Assuming the first style in the list is the primary style for simplicity
        primary_style = self.styles[0] if self.styles else "No Style"
        return f"{self.name}({self.country}) - {primary_style}"

    def special_get_styles(self):
        # Return a list of unique styles
        styles = [style.title() for style in set(self.styles)]
        return styles




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
    judges = models.ManyToManyField('Dancer', related_name='battle_judges', blank=True)
    host = models.ForeignKey('Dancer', on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=10, choices=BATTLE_TYPE_CHOICES, default='1vs1')
    is_7tosmoke = models.BooleanField(default=False)
    # Additional fields specific to Battle can be added here

    def save(self, *args, **kwargs):
        logger.debug(f'Setting type to BATTLE for {self.name}')
        self.event_type = self.BATTLE  # Set the type for the Battle instance
        super().save(*args, **kwargs)
    pass


class Showcase(Event):
    # Additional fields specific to Showcase can be added here
    pass


class Tip(models.Model):
    EVENT_TYPES = [
        ('workshop', 'Workshop'),
        ('battle', 'Battle'),
        ('showcase', 'Showcase'),
    ]

    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    styles = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    level = models.CharField(max_length=13, choices=LEVEL_CHOICES, default='1vs1')
    poster = models.ImageField(upload_to='tip_posters/', null=True, blank=True)
    video = models.FileField(upload_to='tip_videos/', null=True, blank=True)  # If storing video files
    contact_info = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=EVENT_TYPES)

    def verify(self):
        """
        Verify the tip and create an event based on the information provided.
        """
        # Assuming OrganizerProfile has a method to create events
        organizer_profile = settings.AUTH_USER_MODEL.organizerprofile_set.get(contact_info=self.contact_info)

        if organizer_profile:
            event_data = {
                'organizer': organizer_profile,
                'event_type': self.type,
                'name': self.name,
                'date': self.date,
                'location': self.location,
                'description': self.description,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'styles': self.styles,
                'level': self.level,
                'poster': self.poster,
                'video': self.video,
                'is_hidden': False,  # Automatically set to False when verified
            }

            event = Event.objects.create(**event_data)
            return event
        else:
            # Handle case where organizer profile is not found
            return None