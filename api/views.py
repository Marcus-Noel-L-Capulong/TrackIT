from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Course, AttendanceRecord
import json

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
            # Filter records by the requested student_id
            records = AttendanceRecord.objects.filter(student__user_id=student_id)
            
            history = [
                {
                    "course_id": r.course.course_id, 
                    "date": r.date, 
                    "status": r.status
                } for r in records
            ]
            
            # Count how many times the status is 'Absent'
            absences = records.filter(status='Absent').count()
            
            return JsonResponse({
                'student_id': student_id,
                'total_absences': absences,
                'history': history
            }, status=200)
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


@csrf_exempt
def manage_courses(request):
    """ Feature 3: Admin creates a new course """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            instructor = User.objects.get(user_id=data['instructor_id'], role='Instructor')
            
            # Create the course
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