
from django.contrib import admin
from django.urls import path,include
from spotify import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('spotify/',include('spotify.urls')),
    path('',views.home,name='home')
]
if settings.DEBUG :
    urlpatterns += static(settings.STATIC_URL,document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)