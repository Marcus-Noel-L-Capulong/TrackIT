from django.contrib import admin
from django.urls import path, include  # <-- Added 'include' here

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # <-- Added your API router here
]