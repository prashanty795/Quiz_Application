from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from staff import models as SMODEL
from quiz import forms as QFORM


#for showing signup/login button for manager
def managerclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'manager/managerclick.html')

def manager_signup_view(request):
    userForm=forms.ManagerUserForm()
    managerForm=forms.ManagerForm()
    mydict={'userForm':userForm,'managerForm':managerForm}
    if request.method=='POST':
        userForm=forms.ManagerUserForm(request.POST)
        managerForm=forms.ManagerForm(request.POST,request.FILES)
        if userForm.is_valid() and managerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            manager=managerForm.save(commit=False)
            manager.user=user
            manager.save()
            my_manager_group = Group.objects.get_or_create(name='MANAGER')
            my_manager_group[0].user_set.add(user)
        return HttpResponseRedirect('managerlogin')
    return render(request,'manager/managersignup.html',context=mydict)



def is_manager(user):
    return user.groups.filter(name='MANAGER').exists()

@login_required(login_url='managerlogin')
@user_passes_test(is_manager)
def manager_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    'total_staff':SMODEL.Staff.objects.all().count()
    }
    return render(request,'manager/manager_dashboard.html',context=dict)

@login_required(login_url='managerlogin')
@user_passes_test(is_manager)
def manager_quiz_view(request):
    return render(request,'manager/manager_quiz.html')


@login_required(login_url='managerlogin')
@user_passes_test(is_manager)
def manager_add_quiz_view(request):
    courseForm=QFORM.CourseForm()
    if request.method=='POST':
        courseForm=QFORM.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/manager/manager-view-quiz')
    return render(request,'manager/manager_add_quiz.html',{'courseForm':courseForm})

@login_required(login_url='managerlogin')
@user_passes_test(is_manager)
def manager_view_quiz_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request,'manager/manager_view_quiz.html',{'courses':courses})

@login_required(login_url='managerlogin')
@user_passes_test(is_manager)
def delete_quiz_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/manager/manager-view-quiz')

@login_required(login_url='adminlogin')
def manager_question_view(request):
    return render(request,'manager/manager_question.html')

@login_required(login_url='managerlogin')
@user_passes_test(is_manager)
def manager_add_question_view(request):
    questionForm=QFORM.QuestionForm()
    if request.method=='POST':
        questionForm=QFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            course=QMODEL.Course.objects.get(id=request.POST.get('courseID'))
            question.course=course
            question.save()       
        else:
            print("form is invalid")
        return HttpResponseRedirect('/manager/manager-view-question')
    return render(request,'manager/manager_add_question.html',{'questionForm':questionForm})

@login_required(login_url='managerlogin')
@user_passes_test(is_manager)
def manager_upload_question_view(request):
    questionForm=QFORM.QuestionForm()
    if request.method=='POST':
        questionForm=QFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            course=QMODEL.Course.objects.get(id=request.POST.get('courseID'))
            question.course=course
            question.save()       
        else:
            print("form is invalid")
        return HttpResponseRedirect('/manager/manager-view-question')
    return render(request,'manager/manager_upload_question.html',{'questionForm':questionForm})

@login_required(login_url='managerlogin')
@user_passes_test(is_manager)
def manager_view_question_view(request):
    courses= QMODEL.Course.objects.all()
    return render(request,'manager/manager_view_question.html',{'courses':courses})

@login_required(login_url='managerlogin')
@user_passes_test(is_manager)
def see_question_view(request,pk):
    questions=QMODEL.Question.objects.all().filter(course_id=pk)
    return render(request,'manager/see_question.html',{'questions':questions})

@login_required(login_url='managerlogin')
@user_passes_test(is_manager)
def remove_question_view(request,pk):
    question=QMODEL.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/manager/manager-view-question')
