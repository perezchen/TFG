from django.contrib import admin
from .models import Inquilino, Casa, Reserva_restaurante

# Register your models here.
admin.site.register(Inquilino)
admin.site.register(Casa)
admin.site.register(Reserva_restaurante)