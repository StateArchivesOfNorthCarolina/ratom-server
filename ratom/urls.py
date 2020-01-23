from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include

from api.urls import ratom_urlpatterns


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(ratom_urlpatterns)),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        re_path(r"^__debug__/", include(debug_toolbar.urls)),
    ]
