from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Course, AttendanceRecord
from django.contrib.auth.hashers import make_password, check_password
import json

# --- AUTH LOGIC ---
@csrf_exempt
def register_user(request):
    """ Feature: Register a new User/Instructor with Password Hashing """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            name = data.get('name')
            role = data.get('role')
            password = data.get('password')

            if User.objects.filter(user_id=user_id).exists():
                return JsonResponse({'error': 'User ID already exists!'}, status=400)

            # Create the new user with a HASHED password
            User.objects.create(
                user_id=user_id, 
                name=name, 
                role=role,
                password=make_password(password)
            )
            return JsonResponse({'message': 'Account created successfully!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def login_user(request):
    """ Feature: Authenticate a user by checking the hashed password """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            password = data.get('password')

            user = User.objects.get(user_id=user_id)
            
            if check_password(password, user.password):
                return JsonResponse({
                    'message': 'Login successful',
                    'user': {
                        'user_id': user.user_id, 
                        'name': user.name, 
                        'role': user.role
                    }
                }, status=200)
            else:
                return JsonResponse({'error': 'Invalid password!'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# --- ATTENDANCE LOGIC ---
@csrf_exempt
def record_attendance(request):
    """ Feature 1: Instructor records daily attendance """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            course = Course.objects.get(course_id=data['course_id'])
            date = data['date']
            
            records_created = 0
            for item in data['records']:
                student = User.objects.get(user_id=item['student_id'], role='Student')
                AttendanceRecord.objects.create(
                    date=date,
                    status=item['status'],
                    student=student,
                    course=course
                )
                records_created += 1
                
            return JsonResponse({
                'status': 'success', 
                'message': f'Attendance saved successfully for {records_created} students.'
            }, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def view_student_attendance(request, student_id):
    """ Feature 2: Student views their own history """
    if request.method == 'GET':
        try:
            # We use student__user_id to filter by the primary key of the User model
            records = AttendanceRecord.objects.filter(student__user_id=student_id).order_by('-date')
            
            history = [
                {
                    "course_id": r.course.course_id, 
                    "date": r.date.strftime("%Y-%m-%d"), # Formatted for JS compatibility
                    "status": r.status
                } for r in records
            ]
            
            absences = records.filter(status='Absent').count()
            
            return JsonResponse({
                'student_id': student_id,
                'total_absences': absences,
                'history': history
            }, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

# --- COURSE MANAGEMENT LOGIC ---
@csrf_exempt
def manage_courses(request):
    """ Feature 3: Admin creates a new course """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            instructor = User.objects.get(user_id=data['instructor_id'], role='Instructor')
            
            course = Course.objects.create(
                course_id=data['course_id'],
                course_name=data['course_name'],
                instructor=instructor
            )
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Course created successfully.',
                'data': {
                    'course_id': course.course_id, 
                    'course_name': course.course_name
                }
            }, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)