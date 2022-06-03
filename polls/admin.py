from django.contrib import admin
from .models import Person
from .models import reservations
from .models import res_done
from .models import cancel_request,Person_reduce_shift,archive_res_done
admin.site.register(Person)
admin.site.register(reservations)
admin.site.register(res_done)
admin.site.register(cancel_request)
admin.site.register(Person_reduce_shift)
admin.site.register(archive_res_done)