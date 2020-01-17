# from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from ratom.urls import ratom_urlpatterns


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(ratom_urlpatterns)),
]
