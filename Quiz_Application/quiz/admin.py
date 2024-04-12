from django.contrib import admin
from .models import Question
from import_export.admin import ImportExportActionModelAdmin

admin.site.register(Question, ImportExportActionModelAdmin)
