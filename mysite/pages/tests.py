from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Page, ContactMessage

class PagesAPITests(APITestCase):
    def setUp(self):
        self.page = Page.objects.create(slug='about', title='About Us', content='This is the about page.')

    def test_get_page(self):
        url = reverse('page-detail', kwargs={'slug': 'about'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'About Us')

    def test_post_contact_message(self):
        url = reverse('contactmessage-list')
        data = {'name': 'Test User', 'email': 'test@example.com', 'message': 'This is a test message.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(ContactMessage.objects.get().name, 'Test User')
