from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from manager import models as TMODEL
from staff import models as SMODEL
from manager import forms as TFORM
from staff import forms as SFORM
from django.contrib.auth.models import User
from django.contrib.auth import logout



def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')  
    return render(request,'quiz/index.html')


def is_manager(user):
    return user.groups.filter(name='MANAGER').exists()

def is_staff(user):
    return user.groups.filter(name='STAFF').exists()

def afterlogin_view(request):
    if is_staff(request.user):      
        return redirect('staff/staff-dashboard')
                
    elif is_manager(request.user):
        accountapproval=TMODEL.Manager.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('manager/manager-dashboard')
        else:
            return render(request,'manager/manager_wait_for_approval.html')
    else:
        return redirect('admin-dashboard')



def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict={
    'total_staff':SMODEL.Staff.objects.all().count(),
    'total_manager':TMODEL.Manager.objects.all().filter(status=True).count(),
    'total_course':models.Course.objects.all().count(),
    'total_question':models.Question.objects.all().count(),
    }
    return render(request,'quiz/admin_dashboard.html',context=dict)

@login_required(login_url='adminlogin')
def admin_manager_view(request):
    dict={
    'total_manager':TMODEL.Manager.objects.all().filter(status=True).count(),
    'pending_manager':TMODEL.Manager.objects.all().filter(status=False).count(),
    'salary':TMODEL.Manager.objects.all().filter(status=True).aggregate(Sum('salary'))['salary__sum'],
    }
    return render(request,'quiz/admin_manager.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_manager_view(request):
    managers= TMODEL.Manager.objects.all().filter(status=True)
    return render(request,'quiz/admin_view_manager.html',{'managers':managers})


@login_required(login_url='adminlogin')
def update_manager_view(request,pk):
    manager=TMODEL.Manager.objects.get(id=pk)
    user=TMODEL.User.objects.get(id=manager.user_id)
    userForm=TFORM.ManagerUserForm(instance=user)
    managerForm=TFORM.ManagerForm(request.FILES,instance=manager)
    mydict={'userForm':userForm,'managerForm':managerForm}
    if request.method=='POST':
        userForm=TFORM.ManagerUserForm(request.POST,instance=user)
        managerForm=TFORM.ManagerForm(request.POST,request.FILES,instance=manager)
        if userForm.is_valid() and managerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            managerForm.save()
            return redirect('admin-view-manager')
    return render(request,'quiz/update_manager.html',context=mydict)



@login_required(login_url='adminlogin')
def delete_manager_view(request,pk):
    manager=TMODEL.Manager.objects.get(id=pk)
    user=User.objects.get(id=manager.user_id)
    user.delete()
    manager.delete()
    return HttpResponseRedirect('/admin-view-manager')




@login_required(login_url='adminlogin')
def admin_view_pending_manager_view(request):
    managers= TMODEL.Manager.objects.all().filter(status=False)
    return render(request,'quiz/admin_view_pending_manager.html',{'managers':managers})


@login_required(login_url='adminlogin')
def approve_manager_view(request,pk):
    managerSalary=forms.ManagerSalaryForm()
    if request.method=='POST':
        managerSalary=forms.ManagerSalaryForm(request.POST)
        if managerSalary.is_valid():
            manager=TMODEL.Manager.objects.get(id=pk)
            manager.salary=managerSalary.cleaned_data['salary']
            manager.status=True
            manager.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-pending-manager')
    return render(request,'quiz/salary_form.html',{'managerSalary':managerSalary})

@login_required(login_url='adminlogin')
def reject_manager_view(request,pk):
    manager=TMODEL.Manager.objects.get(id=pk)
    user=User.objects.get(id=manager.user_id)
    user.delete()
    manager.delete()
    return HttpResponseRedirect('/admin-view-pending-manager')

@login_required(login_url='adminlogin')
def admin_view_manager_salary_view(request):
    managers= TMODEL.Manager.objects.all().filter(status=True)
    return render(request,'quiz/admin_view_manager_salary.html',{'managers':managers})




@login_required(login_url='adminlogin')
def admin_staff_view(request):
    dict={
    'total_staff':SMODEL.Staff.objects.all().count(),
    }
    return render(request,'quiz/admin_staff.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_staff_view(request):
    staffs= SMODEL.Staff.objects.all()
    return render(request,'quiz/admin_view_staff.html',{'staffs':staffs})



@login_required(login_url='adminlogin')
def update_staff_view(request,pk):
    staff=SMODEL.Staff.objects.get(id=pk)
    user=SMODEL.User.objects.get(id=staff.user_id)
    userForm=SFORM.StaffUserForm(instance=user)
    staffForm=SFORM.StaffForm(request.FILES,instance=staff)
    mydict={'userForm':userForm,'staffForm':staffForm}
    if request.method=='POST':
        userForm=SFORM.StaffUserForm(request.POST,instance=user)
        staffForm=SFORM.StaffForm(request.POST,request.FILES,instance=staff)
        if userForm.is_valid() and staffForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            staffForm.save()
            return redirect('admin-view-staff')
    return render(request,'quiz/update_staff.html',context=mydict)



@login_required(login_url='adminlogin')
def delete_staff_view(request,pk):
    staff=SMODEL.Staff.objects.get(id=pk)
    user=User.objects.get(id=staff.user_id)
    user.delete()
    staff.delete()
    return HttpResponseRedirect('/admin-view-staff')


@login_required(login_url='adminlogin')
def admin_course_view(request):
    return render(request,'quiz/admin_course.html')


@login_required(login_url='adminlogin')
def admin_add_course_view(request):
    courseForm=forms.CourseForm()
    if request.method=='POST':
        courseForm=forms.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-course')
    return render(request,'quiz/admin_add_course.html',{'courseForm':courseForm})


@login_required(login_url='adminlogin')
def admin_view_course_view(request):
    courses = models.Course.objects.all()
    return render(request,'quiz/admin_view_course.html',{'courses':courses})

@login_required(login_url='adminlogin')
def delete_course_view(request,pk):
    course=models.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/admin-view-course')



@login_required(login_url='adminlogin')
def admin_question_view(request):
    return render(request,'quiz/admin_question.html')


@login_required(login_url='adminlogin')
def admin_add_question_view(request):
    questionForm=forms.QuestionForm()
    if request.method=='POST':
        questionForm=forms.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            course=models.Course.objects.get(id=request.POST.get('courseID'))
            question.course=course
            question.save()       
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-question')
    return render(request,'quiz/admin_add_question.html',{'questionForm':questionForm})


@login_required(login_url='adminlogin')
def admin_view_question_view(request):
    courses= models.Course.objects.all()
    return render(request,'quiz/admin_view_question.html',{'courses':courses})

@login_required(login_url='adminlogin')
def view_question_view(request,pk):
    questions=models.Question.objects.all().filter(course_id=pk)
    return render(request,'quiz/view_question.html',{'questions':questions})

@login_required(login_url='adminlogin')
def delete_question_view(request,pk):
    question=models.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/admin-view-question')

@login_required(login_url='adminlogin')
def admin_view_staff_marks_view(request):
    staffs= SMODEL.Staff.objects.all()
    return render(request,'quiz/admin_view_staff_marks.html',{'staffs':staffs})

@login_required(login_url='adminlogin')
def admin_view_marks_view(request,pk):
    courses = models.Course.objects.all()
    response =  render(request,'quiz/admin_view_marks.html',{'courses':courses})
    response.set_cookie('staff_id',str(pk))
    return response

@login_required(login_url='adminlogin')
def admin_check_marks_view(request,pk):
    course = models.Course.objects.get(id=pk)
    staff_id = request.COOKIES.get('staff_id')
    staff= SMODEL.Staff.objects.get(id=staff_id)

    results= models.Result.objects.all().filter(quiz=course).filter(staff=staff)
    return render(request,'quiz/admin_check_marks.html',{'results':results})
    




def aboutus_view(request):
    return render(request,'quiz/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'quiz/contactussuccess.html')
    return render(request, 'quiz/contactus.html', {'form':sub})

def logout_view(request):
    logout(request)     
    return render(request,'quiz/logout.html')


