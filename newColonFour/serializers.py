from rest_framework import serializers
from .models import Event, OrganizerProfile, EventImage, Dancer

class EventSerializer(serializers.ModelSerializer):
    poster_url = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'name', 'poster_url', 'get_number_of_goers', 'get_event_type_display', 'level', 'formatted_date', 'location']

    def get_poster_url(self, obj):
        return obj.poster.url if obj.poster else None

    def get_formatted_date(self, obj):
        return obj.get_formatted_date()

class OrganizerProfileSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = OrganizerProfile
        fields = ['user', 'gdpr_consented', 'is_verified', 'profile_picture_url', 'goings', 'number_of_events', 'instagram_account']

    def get_profile_picture_url(self, obj):
        return obj.get_profile_picture_url()

class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['image']

class DancerSerializer(serializers.ModelSerializer):
    picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Dancer
        fields = ['name', 'country', 'picture_url', 'styles']

    def get_picture_url(self, obj):
        return obj.get_picture_url()
