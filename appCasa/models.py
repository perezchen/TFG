from django.db import models
from django.contrib.auth.models import User

from proyecto_casa import settings


# class ExtraFields(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='extra_fields')
#     university = models.CharField(max_length=255, blank=True, null=True)
#     address = models.CharField(max_length=255, blank=True, null=True)

#     def __str__(self):
#         return self.user.username


class Inquilino(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='extra_fields')
    dni = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Casa(models.Model):
    licencia = models.CharField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    numero_habitaciones = models.IntegerField()
    max_inquilinos = models.IntegerField()
    precio_por_noche = models.DecimalField(max_digits=10, decimal_places=2)
    img_url = models.CharField(max_length=255, default="house.avif")
    url_name = models.CharField(max_length=255, default="casas_panel")

class Reserva(models.Model):
    casa = models.ForeignKey(Casa, on_delete=models.CASCADE)
    inquilino = models.ForeignKey(Inquilino, on_delete=models.CASCADE)
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    num_inquilinos = models.IntegerField(default=1)
    precio_total = models.DecimalField(max_digits=12, decimal_places=2)
    
class Restaurante(models.Model):
    numero_licencia = models.CharField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio_medio = models.DecimalField(max_digits=10, decimal_places=2)
    img_url = models.CharField(max_length=255, default="house.avif")
    url_name = models.CharField(max_length=255, default="index")

    def __str__(self):
        return self.nombre
    
class Reserva_restaurante(models.Model):
    inquilino = models.ForeignKey(Inquilino, on_delete=models.CASCADE, default="1")
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, default="1")
    fecha_reserva = models.DateField()
    hora_reserva = models.TimeField()
    num_comensales = models.IntegerField(default=11)

    def __str__(self):
        return f'Reserva para {self.inquilino} el {self.fecha_reserva} a las {self.hora_reserva}'


class Contrato(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    documento_pdf = models.BinaryField()

class Pago(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField()
    metodo_pago = models.CharField(max_length=255)


class Mensaje(models.Model):
    inquilino = models.ForeignKey(Inquilino, on_delete=models.CASCADE)
    id_admin = models.IntegerField(null=True, blank=True)
    texto = models.TextField()
    fecha_hora = models.DateTimeField()

class Evaluacion(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    calificacion = models.IntegerField(null=True, blank=True)
    comentario = models.TextField(blank=True, null=True)
    fecha_evaluacion = models.DateField(null=True, blank=True)
