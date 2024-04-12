from django.urls import path
from staff import views
from django.contrib.auth.views import LoginView

urlpatterns = [
path('staff/staffclick', views.staffclick_view),
path('staff/stafflogin', LoginView.as_view(template_name='staff/stafflogin.html'),name='stafflogin'),
path('staff/staffsignup', views.staff_signup_view,name='staffsignup'),
path('staff/staff-dashboard', views.staff_dashboard_view,name='staff-dashboard'),
path('staff/staff-quiz', views.staff_quiz_view,name='staff-quiz'),
path('take-quiz/<int:pk>', views.take_quiz_view,name='take-quiz'),
path('start-quiz/<int:pk>', views.start_quiz_view,name='start-quiz'),

path('staff/calculate-marks', views.calculate_marks_view,name='calculate-marks'),
path('staff/view-result', views.view_result_view,name='view-result'),
path('check-marks/<int:pk>', views.check_marks_view,name='check-marks'),
path('staff/staff-marks', views.staff_marks_view,name='staff-marks'),
]