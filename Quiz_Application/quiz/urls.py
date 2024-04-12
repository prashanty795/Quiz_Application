from django.urls import path
from quiz import views
from django.contrib.auth.views import LogoutView,LoginView

urlpatterns = [
    path('',views.home_view,name=''),
    path('logout', views.logout_view ,name='logout'),
    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),
    path('afterlogin', views.afterlogin_view,name='afterlogin'),



    path('adminclick', views.adminclick_view),
    path('adminlogin', LoginView.as_view(template_name='quiz/adminlogin.html'),name='adminlogin'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),
    path('admin-manager', views.admin_manager_view,name='admin-manager'),
    path('admin-view-manager', views.admin_view_manager_view,name='admin-view-manager'),
    path('update-manager/<int:pk>', views.update_manager_view,name='update-manager'),
    path('delete-manager/<int:pk>', views.delete_manager_view,name='delete-manager'),
    path('admin-view-pending-manager', views.admin_view_pending_manager_view,name='admin-view-pending-manager'),
    path('admin-view-manager-salary', views.admin_view_manager_salary_view,name='admin-view-manager-salary'),
    path('approve-manager/<int:pk>', views.approve_manager_view,name='approve-manager'),
    path('reject-manager/<int:pk>', views.reject_manager_view,name='reject-manager'),

    path('admin-staff', views.admin_staff_view,name='admin-staff'),
    path('admin-view-staff', views.admin_view_staff_view,name='admin-view-staff'),
    path('admin-view-staff-marks', views.admin_view_staff_marks_view,name='admin-view-staff-marks'),
    path('admin-view-marks/<int:pk>', views.admin_view_marks_view,name='admin-view-marks'),
    path('admin-check-marks/<int:pk>', views.admin_check_marks_view,name='admin-check-marks'),
    path('update-staff/<int:pk>', views.update_staff_view,name='update-staff'),
    path('delete-staff/<int:pk>', views.delete_staff_view,name='delete-staff'),

    path('admin-course', views.admin_course_view,name='admin-course'),
    path('admin-add-course', views.admin_add_course_view,name='admin-add-course'),
    path('admin-view-course', views.admin_view_course_view,name='admin-view-course'),
    path('delete-course/<int:pk>', views.delete_course_view,name='delete-course'),

    path('admin-question', views.admin_question_view,name='admin-question'),
    path('admin-add-question', views.admin_add_question_view,name='admin-add-question'),
    path('admin-view-question', views.admin_view_question_view,name='admin-view-question'),
    path('view-question/<int:pk>', views.view_question_view,name='view-question'),
    path('delete-question/<int:pk>', views.delete_question_view,name='delete-question'),


]
