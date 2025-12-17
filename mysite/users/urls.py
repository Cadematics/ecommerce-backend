from django.urls import path
from .views import (
    RegisterView,
    LogoutView,
    UserProfileView,
    AddressListCreateView,
    AddressDetailView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('me/addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('me/addresses/<int:id>/', AddressDetailView.as_view(), name='address-detail'),
]
