from rest_framework import serializers
from .models import Page, ContactMessage

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('slug', 'title', 'content')

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'message')
