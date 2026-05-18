from django.contrib import admin
from .models import User, Course, AttendanceRecord

# Tell Django to show these in the admin panel
admin.site.register(User)
admin.site.register(Course)
admin.site.register(AttendanceRecord)