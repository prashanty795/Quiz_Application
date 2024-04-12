from django.urls import path
from manager import views
from django.contrib.auth.views import LoginView

urlpatterns = [
path('manager/managerclick', views.managerclick_view),
path('manager/managerlogin', LoginView.as_view(template_name='manager/managerlogin.html'),name='managerlogin'),
path('manager/managersignup', views.manager_signup_view,name='managersignup'),
path('manager/manager-dashboard', views.manager_dashboard_view,name='manager-dashboard'),
path('manager/manager-quiz', views.manager_quiz_view,name='manager-quiz'),
path('manager/manager-add-quiz', views.manager_add_quiz_view,name='manager-add-quiz'),
path('manager/manager-view-quiz', views.manager_view_quiz_view,name='manager-view-quiz'),
path('delete-quiz/<int:pk>', views.delete_quiz_view,name='delete-quiz'),


path('manager/manager-question', views.manager_question_view,name='manager-question'),
path('manager/manager-add-question', views.manager_add_question_view,name='manager-add-question'),
path('manager/manager-upload-question', views.manager_upload_question_view,name='manager-upload-question'),
path('manager/manager-view-question', views.manager_view_question_view,name='manager-view-question'),
path('see-question/<int:pk>', views.see_question_view,name='see-question'),
path('remove-question/<int:pk>', views.remove_question_view,name='remove-question'),
]