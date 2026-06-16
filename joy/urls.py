from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('administrative-security-activities501B64/', admin.site.urls),
    path('', include('shop_project.urls')),  # rename 'shop_project' if your app is named differently
]

# Only needed for local dev with non-Cloudinary media (Cloudinary serves its own URLs in prod)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
