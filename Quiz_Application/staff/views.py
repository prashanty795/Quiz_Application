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
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'staff/take_quiz.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

@login_required(login_url='stafflogin')
@user_passes_test(is_staff)
def start_quiz_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    questions=QMODEL.Question.objects.all().filter(course=course)
    if request.method=='POST':
        pass
    response= render(request,'staff/start_quiz.html',{'course':course,'questions':questions})
    response.set_cookie('course_id',course.id)
    return response


@login_required(login_url='stafflogin')
@user_passes_test(is_staff)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course=QMODEL.Course.objects.get(id=course_id)
        
        total_marks=0
        questions=QMODEL.Question.objects.all().filter(course=course)
        for i in range(len(questions)):
            
            selected_ans = request.COOKIES.get(str(i+1))
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks = total_marks + questions[i].marks
        staff = models.Staff.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks=total_marks
        result.quiz=course
        result.staff=staff
        result.save()

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
  