from django.urls import path
from . import views

urlpatterns = [
    path('attendance/record/', views.record_attendance, name='record_attendance'),
    path('attendance/student/<str:student_id>/', views.view_student_attendance, name='view_attendance'),
    path('courses/manage/', views.manage_courses, name='manage_courses'),
]