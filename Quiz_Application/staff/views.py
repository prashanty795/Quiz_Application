from django.shortcuts import render,redirect,reverse
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
    questions = list(QMODEL.Question.objects.filter(course=course))
    shuffle(questions) 
    questions = questions[:course.question_number]
    
    # Calculate remaining time
    quiz_start_time_key = f"quiz_start_time_{course.id}"
    if quiz_start_time_key not in request.session:
        request.session[quiz_start_time_key] = timezone.now().isoformat()
    quiz_start_time = timezone.datetime.fromisoformat(request.session[quiz_start_time_key])
    total_time = course.minutes
    elapsed_time = (timezone.now() - quiz_start_time).seconds // 60
    remaining_time = max(total_time - elapsed_time, 0)

    response = render(request, 'staff/start_quiz.html', {'course': course, 'questions': questions, 'remaining_time': remaining_time})
    response.set_cookie('course_id', course.id)
    return response


def calculate_marks_view(request):
    if 'course_id' in request.COOKIES:
        course_id = request.COOKIES['course_id']
        course = QMODEL.Course.objects.get(id=course_id)
        
        total_marks = 0
        questions = QMODEL.Question.objects.filter(course=course)
        for i, question in enumerate(questions):
            selected_ans = request.COOKIES.get(f'q_{i+1}')
            if selected_ans == question.answer:
                total_marks += question.marks
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
  