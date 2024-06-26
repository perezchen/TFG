# Generated by Django 5.0.4 on 2024-06-09 23:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Casa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('licencia', models.CharField(max_length=255, unique=True)),
                ('nombre', models.CharField(max_length=255)),
                ('direccion', models.CharField(max_length=255)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('numero_habitaciones', models.IntegerField()),
                ('max_inquilinos', models.IntegerField()),
                ('precio_noche_persona', models.DecimalField(decimal_places=2, default=50.0, max_digits=12)),
                ('img_url', models.CharField(default='house.avif', max_length=255)),
                ('url_name', models.CharField(default='casas_panel', max_length=255)),
                ('dias_cancel', models.IntegerField(default=31)),
            ],
        ),
        migrations.CreateModel(
            name='Restaurante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_licencia', models.CharField(max_length=255, unique=True)),
                ('nombre', models.CharField(max_length=255)),
                ('direccion', models.CharField(max_length=255)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('precio_medio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('img_url', models.CharField(default='house.avif', max_length=255)),
                ('url_name', models.CharField(default='index', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Conversacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asunto', models.CharField(max_length=255)),
                ('participantes', models.ManyToManyField(related_name='conversaciones', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Inquilino',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dni', models.CharField(max_length=255, unique=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='extra_fields', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Mensaje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField()),
                ('fecha_hora', models.DateTimeField(auto_now_add=True)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes_enviados', to=settings.AUTH_USER_MODEL)),
                ('conversacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes', to='appCasa.conversacion')),
            ],
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_entrada', models.DateField()),
                ('fecha_salida', models.DateField()),
                ('num_inquilinos', models.IntegerField(default=1)),
                ('num_menores', models.IntegerField(default=0)),
                ('precio_total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('cancelada', models.BooleanField(default=False)),
                ('casa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appCasa.casa')),
                ('inquilino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appCasa.inquilino')),
            ],
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_pago', models.DateField()),
                ('metodo_pago', models.CharField(max_length=255)),
                ('reserva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appCasa.reserva')),
            ],
        ),
        migrations.CreateModel(
            name='Evaluacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calificacion', models.IntegerField(blank=True, null=True)),
                ('comentario', models.TextField(blank=True, null=True)),
                ('fecha_evaluacion', models.DateField(blank=True, null=True)),
                ('reserva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appCasa.reserva')),
            ],
        ),
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('documento_pdf', models.BinaryField()),
                ('reserva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appCasa.reserva')),
            ],
        ),
        migrations.CreateModel(
            name='Reserva_restaurante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_reserva', models.DateField()),
                ('hora_reserva', models.TimeField()),
                ('num_comensales', models.IntegerField(default=11)),
                ('inquilino', models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to='appCasa.inquilino')),
                ('restaurante', models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to='appCasa.restaurante')),
            ],
        ),
    ]
