from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PageViewSet, ContactMessageViewSet

router = DefaultRouter()
router.register(r'pages', PageViewSet)
router.register(r'contact', ContactMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
