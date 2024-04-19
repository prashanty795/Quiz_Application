from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from manager import models as TMODEL
from random import shuffle
from django.utils import timezone
from django.utils.timezone import datetime
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.http import JsonResponse


#for showing signup/login button for staff
def staffclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'staff/staffclick.html')

def staff_signup_view(request):
    userForm=forms.StaffUserForm()
    staffForm=forms.StaffForm()
    mydict={'userForm':userForm,'staffForm':staffForm}
    if request.method=='POST':
        userForm=forms.StaffUserForm(request.POST)
        staffForm=forms.StaffForm(request.POST,request.FILES)
        if userForm.is_valid() and staffForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            staff=staffForm.save(commit=False)
            staff.user=user
            staff.save()
            my_staff_group = Group.objects.get_or_create(name='STAFF')
            my_staff_group[0].user_set.add(user)
        return HttpResponseRedirect('stafflogin')
    return render(request,'staff/staffsignup.html',context=mydict)

def is_staff(user):
    return user.groups.filter(name='STAFF').exists()

@login_required(login_url='stafflogin')
@user_passes_test(is_staff)
def staff_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'staff/staff_dashboard.html',context=dict)

@login_required(login_url='stafflogin')
@user_passes_test(is_staff)
def staff_quiz_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'staff/staff_quiz.html',{'courses':courses})

@login_required(login_url='stafflogin')
@user_passes_test(is_staff)
def take_quiz_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=course.question_number
    total_marks=course.total_marks
    minutes=course.minutes
    
    return render(request,'staff/take_quiz.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks,'minutes':minutes})

@login_required(login_url='stafflogin')
@user_passes_test(is_staff)
def start_quiz_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    quiz_start_time_key = f"quiz_start_time_{course.id}"
    questions = list(QMODEL.Question.objects.filter(course=course))
    shuffle(questions)
    questions = questions[:course.question_number]
    
    if quiz_start_time_key not in request.session:
        
        request.session[quiz_start_time_key] = timezone.now().isoformat()
        request.session['course_id'] = course.id
        request.session.save()

    quiz_start_time = timezone.datetime.fromisoformat(request.session[quiz_start_time_key])
    total_time = course.minutes * 60
    elapsed_time = (timezone.now() - quiz_start_time).seconds
    remaining_time = max(total_time - elapsed_time, 0)

    return render(request, 'staff/start_quiz.html', {'course': course, 'questions': questions, 'remaining_time': remaining_time})


@login_required(login_url='stafflogin')
@user_passes_test(is_staff)
def check_timer(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    quiz_start_time_key = f"quiz_start_time_{course.id}"
    
    if quiz_start_time_key in request.session:
        quiz_start_time = timezone.datetime.fromisoformat(request.session[quiz_start_time_key])
        total_time = course.minutes * 60
        elapsed_time = (timezone.now() - quiz_start_time).seconds
        remaining_time = max(total_time - elapsed_time, 0)
        
        if remaining_time <= 0:
            del request.session[quiz_start_time_key]
            request.session.save() 
            return JsonResponse({'time_up': True, 'remaining_time': 0})
        else:
            return JsonResponse({'time_up': False, 'remaining_time': remaining_time})
    else:
        return JsonResponse({'error': 'Quiz session not found'})
    

def calculate_marks(request):
    if request.method == 'POST':
        course_id = request.session.get('course_id')

        # Retrieve questions for the course
        course = QMODEL.Course.objects.get(id=course_id)
        questions = QMODEL.Question.objects.filter(course=course)

        for question in questions:
            selected_answer_key = f'selected_answer_{question.id}'
            selected_answer = request.POST.get(selected_answer_key)

        # Clear session data after processing
        del request.session['course_id']
        request.session.save()




def calculate_marks_view(request):
    if 'course_id' in request.COOKIES:
        course_id = request.COOKIES['course_id']
        course = QMODEL.Course.objects.get(id=course_id)
        
        total_marks = 0
        question_responses = []

        questions = QMODEL.Question.objects.filter(course=course)
        for i, question in enumerate(questions):
            selected_ans = request.COOKIES.get(f'q_{i+1}')
            is_correct = selected_ans == question.answer
            if is_correct:
                total_marks += question.marks
            
            question_response = {
                'question_text': question.question,
                'selected_answer': selected_ans,
                'correct_answer': question.answer,
                'is_correct': is_correct
            }
            question_responses.append(question_response)

        name = request.user.first_name
        course_name = course.course_name

        send_quiz_report(question_responses, course_name, total_marks, name)

        staff = models.Staff.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks=total_marks
        result.quiz=course
        result.staff=staff
        result.save()

        # Delete quiz start time from session
        quiz_start_time_key = f"quiz_start_time_{course.id}"
        if quiz_start_time_key in request.session:
            del request.session[quiz_start_time_key]
            request.session.save()

        return HttpResponseRedirect('view-result')

def send_quiz_report(question_responses, course_name, total_marks, name):
    html_content = render_to_string('quiz_report.html',{'question_responses':question_responses, 'course':course_name, 'total_marks':total_marks, 'person_name':name})
    subject = f'{name} Quiz Report for {course_name}'
    plain_message = strip_tags(html_content)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = ['prashanty795@gmail.com', 'prashanty1229@gmail.com']
    send_mail(subject, plain_message, from_email, to_email, html_message=html_content)

@login_required(login_url='stafflogin')
@user_passes_test(is_staff)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'staff/view_result.html',{'courses':courses})
    

@login_required(login_url='stafflogin')
@user_passes_test(is_staff)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    staff = models.Staff.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(quiz=course).filter(staff=staff)
    return render(request,'staff/check_marks.html',{'results':results})

@login_required(login_url='stafflogin')
@user_passes_test(is_staff)
def staff_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'staff/staff_marks.html',{'courses':courses})
  