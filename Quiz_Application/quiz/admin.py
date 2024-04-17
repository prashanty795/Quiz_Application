from django.contrib import admin
from .models import Question, Course, Result
from import_export.admin import ImportExportActionModelAdmin

admin.site.register(Question, ImportExportActionModelAdmin)
admin.site.register(Course)
admin.site.register(Result)
