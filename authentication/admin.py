from django.contrib import admin
from authentication.models import Sport
from authentication.models import Session

# Register your models here.
admin.site.register(Sport)
admin.site.register(Session)