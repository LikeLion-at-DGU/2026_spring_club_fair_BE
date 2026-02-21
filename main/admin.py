from django.contrib import admin
from .models import *


admin.site.register(Schedule)
admin.site.register(Location)
admin.site.register(Division)
admin.site.register(Booth)
admin.site.register(BoothImage)
admin.site.register(TimeTable)