# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('', include('core.urls')),  # Your core app
    path('products/', include('products.urls')),  # Your core app
    # backend/urls.py (add this line)
    path('cart/', include('cart.urls')),
    path('checkout/', include('checkout.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)