
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes
    path('api/', include('pages.urls')),
    path('api/auth/', include('users.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/store/', include('store.urls')),

    # Admin API routes
    path('api/admin/', include('admin_api.urls')),

    # Default to store URLs if no other route is matched
    path('', include('store.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
