from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Course, AttendanceRecord
from django.contrib.auth.hashers import make_password, check_password
import json
import csv
import io
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

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
                student_id = item.get('student_id')
                try:
                    student = User.objects.get(user_id=student_id, role='Student')
                except User.DoesNotExist:
                    return JsonResponse({
                        'status': 'error', 
                        'message': f"Student with ID '{student_id}' does not exist or is not a student."
                    }, status=400)
                    
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

# --- ROSTER MANAGEMENT LOGIC ---
@csrf_exempt
def update_course_roster(request):
    """ Feature: Admin adds or removes students from a course roster """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
            student_id = data.get('student_id')
            action = data.get('action') # 'add' or 'remove'
            
            course = Course.objects.get(course_id=course_id)
            student = User.objects.get(user_id=student_id, role='Student')
            
            if action == 'add':
                course.students.add(student)
                message = f"Student {student.name} added to {course.course_name}."
            elif action == 'remove':
                course.students.remove(student)
                message = f"Student {student.name} removed from {course.course_name}."
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)
                
            return JsonResponse({'message': message}, status=200)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_course_roster(request, course_id):
    """ Helper: Get all students in a course and all students NOT in the course """
    try:
        course = Course.objects.get(course_id=course_id)
        enrolled_students = course.students.all()
        all_students = User.objects.filter(role='Student')
        
        enrolled_list = [{'user_id': s.user_id, 'name': s.name} for s in enrolled_students]
        available_list = [{'user_id': s.user_id, 'name': s.name} for s in all_students if s not in enrolled_students]
        
        return JsonResponse({
            'course_id': course_id,
            'course_name': course.course_name,
            'enrolled': enrolled_list,
            'available': available_list
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --- REPORTING LOGIC ---
def export_attendance_report(request):
    """ Feature: Instructor exports monthly attendance report in CSV or PDF """
    if request.method == 'GET':
        try:
            course_id = request.GET.get('course_id')
            month = request.GET.get('month')
            year = request.GET.get('year')
            export_format = request.GET.get('format', 'csv').lower()
            
            if not course_id or not month or not year:
                return JsonResponse({'error': 'Missing required parameters: course_id, month, year'}, status=400)

            course = Course.objects.get(course_id=course_id)
            records = AttendanceRecord.objects.filter(
                course=course,
                date__month=month,
                date__year=year
            ).order_by('date', 'student__name')
            
            if export_format == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="attendance_{course_id}_{year}_{month}.csv"'
                
                writer = csv.writer(response)
                writer.writerow(['Date', 'Student ID', 'Student Name', 'Status'])
                for record in records:
                    writer.writerow([record.date, record.student.user_id, record.student.name, record.status])
                return response
                
            elif export_format == 'pdf':
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                
                elements.append(Paragraph(f"Attendance Report: {course.course_name} ({course_id})", styles['Title']))
                elements.append(Paragraph(f"Month: {month}/{year}", styles['Heading2']))
                
                data = [['Date', 'Student ID', 'Student Name', 'Status']]
                for record in records:
                    data.append([str(record.date), record.student.user_id, record.student.name, record.status])
                
                if len(data) > 1:
                    t = Table(data)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(t)
                else:
                    elements.append(Paragraph("No records found for this period.", styles['Normal']))

                doc.build(elements)
                
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="attendance_{course_id}_{year}_{month}.pdf"'
                response.write(buffer.getvalue())
                buffer.close()
                return response
            else:
                return JsonResponse({'error': 'Unsupported format'}, status=400)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_course_attendance(request, course_id):
    """ Feature: View students by attendance status for a specific course """
    if request.method == 'GET':
        try:
            from datetime import date
            target_date = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
            status_filter = request.GET.get('status') # Optional: Present, Absent, Late
            
            query = AttendanceRecord.objects.filter(
                course_id=course_id, 
                date=target_date
            )
            
            if status_filter and status_filter != 'All':
                query = query.filter(status=status_filter)
                
            records = query.select_related('student')
            
            students = [
                {
                    'user_id': r.student.user_id,
                    'name': r.student.name,
                    'status': r.status
                } for r in records
            ]
            
            return JsonResponse({
                'course_id': course_id,
                'date': target_date,
                'status_filter': status_filter,
                'records': students
            }, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)