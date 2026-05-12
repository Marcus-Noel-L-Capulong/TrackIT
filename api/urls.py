from django.urls import path
from . import views

urlpatterns = [
    # AUTH ENDPOINTS
    # These match your API_BASE_URL: http://127.0.0.1:8000/api/users/
    path('users/register/', views.register_user, name='register_user'),
    path('users/login/', views.login_user, name='login_user'),

    # STUDENT DASHBOARD ENDPOINT
    # Updated to match the fetch call in your student_dashboard.html
    path('users/attendance/<str:student_id>/', views.view_student_attendance, name='view_student_attendance'),

    # INSTRUCTOR/ADMIN ENDPOINTS
    path('attendance/record/', views.record_attendance, name='record_attendance'),
    path('courses/manage/', views.manage_courses, name='manage_courses'),
]