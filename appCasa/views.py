from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from .models import Casa, Inquilino, Reserva, Reserva_restaurante, Restaurante
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache
from django.contrib import messages


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        dni = request.POST['dni']
        address = request.POST['address']
        user = User.objects.create_user(
            username=username, email=email, password=password)
        Inquilino.objects.create(user=user, dni=dni, address=address)
        return redirect('login')


def check_is_superuser(user):
    return user.is_superuser

def success_view(request):
    return render(request, 'success.html')

def error_view(request):
    return render(request, 'error.html')

@login_required
def index_view(request):
    return render(request, 'index.html')


@login_required
def contact_view(request):
    return render(request, 'contact.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return HttpResponse("Login fallido. Intente de nuevo.")
    return render(request, 'login.html')


def logOut_view(request):
    logout(request)
    return render(request, 'login.html')


# @login_required
# def reserve_view(request, casa_id):
#     if request.method == 'POST':
#         # Coger valores con http de la página web
#         entrada = request.POST.get('fecha_entrada')
#         salida = request.POST.get('fecha_salida')
#         num_inquilinos = request.POST.get('rangeValue')
#         num_inquilinos = int(num_inquilinos)  # Convertimos a int la cadena

#         casa_reserva = get_object_or_404(Casa, id=casa_id)

#         # Obtener el inquilino desde el usuario actual
#         inquilino = get_object_or_404(Inquilino, user=request.user)

#         precio_reserva = num_inquilinos * 50

#         # Crear la reserva
#         Reserva.objects.create(
#             casa=casa_reserva,
#             inquilino=inquilino,
#             fecha_entrada=entrada,
#             fecha_salida=salida,
#             num_inquilinos=num_inquilinos,
#             precio_total=precio_reserva
#         )

#         print(
#             f"Fecha entrada: {entrada}\n Fecha salida: {salida} \n Num Inquilinos: {num_inquilinos} ")

#         return redirect('success')

@login_required
def payment_view(request):
    if request.method == 'POST':
        payment_successful = True
        # Procesa el pago
        if payment_successful:
            # Establecer el flag de pago como exitoso en la sesión
            request.session['payment_successful'] = True
            casa_id = request.session['reservation_data']['casa_id']
            return redirect('reserve', casa_id=casa_id)
        else:
            return redirect('error')
    return render(request, 'payment.html')

@login_required
def reserve_view(request, casa_id):
    if request.method == 'POST':
        
        request.session['reservation_data'] = {
            'fecha_entrada': request.POST.get('fecha_entrada'),
            'fecha_salida': request.POST.get('fecha_salida'),
            'num_inquilinos': request.POST.get('rangeValue'),
            'casa_id': casa_id
        }
        return render(request, 'payment.html')
    
    elif 'payment_successful' in request.session and request.session['payment_successful']:
        # Si el pago fue exitoso, procede a crear la reserva
        reservation_data = request.session.get('reservation_data')
        casa_reserva = get_object_or_404(Casa, id=reservation_data['casa_id'])
        inquilino = get_object_or_404(Inquilino, user=request.user)
        
        try:
            Reserva.objects.create(
                casa=casa_reserva,
                inquilino=inquilino,
                fecha_entrada=reservation_data['fecha_entrada'],
                fecha_salida=reservation_data['fecha_salida'],
                num_inquilinos=int(reservation_data['num_inquilinos']),
                precio_total=int(reservation_data['num_inquilinos']) * 50
            )
        except Exception as e:
            messages.error(request, f"Error al crear la reserva: {e}")
            return render(request, 'error.html')
        
        # Limpia la sesión
        del request.session['reservation_data']
        del request.session['payment_successful']
        return redirect('success')
    else:
        # Mostrar formulario de reserva inicial o manejar error de pago
        return render(request, 'casas/casaPanel.html', {'casa_id': casa_id})

# Vistas casas

@login_required
def casas_panel(request):
    casas = Casa.objects.all()
    for casa in casas:
        print(casa.img_url)
    return render(request, 'casas/casasPanel.html', {'casas': casas})

@login_required
def casa_rio_view(request):
    casa = get_object_or_404(Casa, nombre='Casa Rio')

    return render(request, 'casas/casaRio.html', {'casa': casa})


@login_required
def casa_luisa_view(request):
    casa = get_object_or_404(Casa, nombre='Casa Luisa')

    return render(request, 'casas/casaLuisa.html', {'casa': casa})

@login_required
@never_cache
def casa_paco_view(request):
    casa = get_object_or_404(Casa, nombre='Casa Paco')

    return render(request, 'casas/casaPaco.html', {'casa': casa})


@login_required
def api_reservas(request, casa_id):
    casa = get_object_or_404(Casa, id=casa_id)
    reservas = Reserva.objects.filter(casa=casa)
    data = [{
        'title': 'Reservado',
        'start': reserva.fecha_entrada.strftime('%Y-%m-%d'),
        'end': reserva.fecha_salida.strftime('%Y-%m-%d'),
    } for reserva in reservas]
    return JsonResponse(data, safe=False)





# Vistas Restaurantes
@login_required
def restaurant_view(request):
    return render(request, 'bares/restaurant.html')


@login_required
def bar_paco_view(request):
    restaurante = get_object_or_404(Restaurante, nombre="Bar Paco")

    return render(request, 'bares/barPaco.html', {'restaurante': restaurante})


@login_required
def bar_loscanillas_view(request):
    restaurante = get_object_or_404(Restaurante, nombre="Bar Los Canillas")

    return render(request, 'bares/barLoscanillas.html', {'restaurante': restaurante})


@login_required
def api_restaurante(request, restaurante_licencia):
    restaurante = get_object_or_404(
        Restaurante, numero_licencia=restaurante_licencia)
    inquilino = request.user.extra_fields
    reservas = Reserva_restaurante.objects.filter(
        restaurante=restaurante, inquilino=inquilino)
    data = [{
        'title': 'Reservado',
        'start': reserva.fecha_reserva.strftime('%Y-%m-%d'),
    } for reserva in reservas]

    print(data)
    return JsonResponse(data, safe=False)


@login_required
def reserva_restaurante(request, restaurante_licencia):
    if request.method == 'POST':
        # Coger valores con http de la página web
        fecha_reserva = request.POST.get('fecha_reserva')
        hora_reserva = request.POST.get('hora_reserva')
        num_comensales = request.POST.get('rangeValue')
        num_comensales = int(num_comensales)  # Convertimos a int la cadena

        restaurante = get_object_or_404(
            Restaurante, numero_licencia=restaurante_licencia)

        # Obtener el inquilino desde el usuario actual
        inquilino = get_object_or_404(Inquilino, user=request.user)

        # Crear la reserva
        Reserva_restaurante.objects.create(
            inquilino=inquilino,
            restaurante=restaurante,
            fecha_reserva=fecha_reserva,
            hora_reserva=hora_reserva
        )

        print(
            f"Fecha entrada: {fecha_reserva}\n Hora reserva: {hora_reserva} \n Num Comensales: {num_comensales} ")

        return redirect('success')


# vista administrador
@user_passes_test(check_is_superuser)
def admin_panel_view(request):
    return render(request, 'admin/adminPanel.html')


# admin view casas
@user_passes_test(check_is_superuser)
def admin_casas_view(request):
    casas = Casa.objects.all()
    return render(request, 'admin/adminCasas.html', {'casas': casas})

# admin view inquilinos


@user_passes_test(check_is_superuser)
def admin_inquilino_view(request):
    inquilinos = Inquilino.objects.all()
    return render(request, 'admin/adminInquilinos.html', {'inquilinos': inquilinos})

# admin view restaurantes


@user_passes_test(check_is_superuser)
def admin_restaurantes_view(request):
    restaurantes = Restaurante.objects.all()
    return render(request, 'admin/adminRestaurantes.html', {'restaurantes': restaurantes})

# admin view reservas


@user_passes_test(check_is_superuser)
def admin_reservas_view(request):
    reservas = Reserva.objects.all()
    return render(request, 'admin/adminReservas.html', {'reservas': reservas})

# admin view reservas restaurantes


@user_passes_test(check_is_superuser)
def admin_reservas_restaurantes_view(request):
    reservas = Reserva_restaurante.objects.all()
    return render(request, 'admin/adminReservasRestaurantes.html', {'reservas': reservas})

# Vista CUD


@user_passes_test(check_is_superuser)
def create_object_view(request, tipo_objeto):

    if request.method == 'POST':
        if tipo_objeto == 'casa':
            nombre = request.POST.get('nombre')
            direccion = request.POST.get('direccion')
            licencia = request.POST.get('licencia')
            descripcion = request.POST.get('descripcion')
            num_habitaciones = request.POST.get('num_habitaciones')
            max_inquilinos = request.POST.get('max_inquilinos')
            precio_noche = request.POST.get('precio_noche')
            img_url = request.POST.get('img_url')
            url_name = request.POST.get('url_name')
            Casa.objects.create(licencia=licencia, nombre=nombre, direccion=direccion, descripcion=descripcion,
                                numero_habitaciones=num_habitaciones, max_inquilinos=max_inquilinos, precio_por_noche=precio_noche, img_url=img_url, url_name=url_name)
            return redirect('admin_casas')

        elif tipo_objeto == 'inquilino':
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']
            dni = request.POST['dni']
            address = request.POST['address']
            user = User.objects.create_user(
                username=username, email=email, password=password)
            Inquilino.objects.create(user=user, dni=dni, address=address)
            return redirect('admin_inquilinos')

        elif tipo_objeto == 'restaurante':
            numero_licencia = request.POST['num_licencia']
            nombre = request.POST['nombre']
            direccion = request.POST['direccion']
            descripcion = request.POST['descripcion']
            precio_medio = request.POST['precio_medio']
            Restaurante.objects.create(numero_licencia=numero_licencia, nombre=nombre,
                                       direccion=direccion, descripcion=descripcion, precio_medio=precio_medio)
            return redirect('admin_restaurantes')

    return render(request, 'admin/createObject.html', {'tipo_objeto': tipo_objeto})


@user_passes_test(check_is_superuser)
def update_object_view(request, tipo_objeto, object_id):
    # Esta parte sera la misma ara todos los objetods que vegan, ya que es para renderizar los datos, asi nos ahorramos repetirla en cada if
    models = {
        'casa': Casa,
        'inquilino': Inquilino
    }
    # Obtener el modelo correcto para el tipo de objeto
    if tipo_objeto in models:
        model = models[tipo_objeto]
    else:
        return render(request, 'error.html', {'message': 'Tipo de objeto no válido'})
    # Obtener el objeto
    object = get_object_or_404(model, id=object_id)

    if request.method == 'POST':
        # aunque sea redundante, lo hacemos parfa tener mas constancia de por donde va nuestro codigo
        if tipo_objeto == 'casa':
            casa = get_object_or_404(Casa, id=object_id)
            casa.nombre = request.POST.get('nombre')
            casa.licencia = request.POST.get('licencia')
            casa.direccion = request.POST.get('direccion')
            casa.descripcion = request.POST.get('descripcion')
            casa.numero_habitaciones = request.POST.get('num_habitaciones')
            casa.max_inquilinos = request.POST.get('max_inquilinos')
            casa.precio_por_noche = request.POST.get('precio_noche')
            casa.img_url = request.POST.get('img_url')
            casa.url_name = request.POST.get('url_name')
            casa.save()
            return redirect('admin_casas')
        elif tipo_objeto == 'inquilino':
            inquilino = get_object_or_404(Inquilino, id=object_id)
            user = inquilino.user
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            # ¡Importante! No actualizar la contraseña así sin más, considera usar set_password
            nueva_contraseña = request.POST.get('password')
            if nueva_contraseña:
                user.set_password(nueva_contraseña)
            user.save()
            inquilino.dni = request.POST.get('dni')
            inquilino.address = request.POST.get('address')
            inquilino.save()
            return redirect('admin_inquilinos')

    return render(request, 'admin/updateObject.html', {'object': object, 'tipo_objeto': tipo_objeto})


@user_passes_test(check_is_superuser)
def delete_object_view(request, tipo_objeto, object_id):
    # Esta parte sera la misma para todos los objetods que vegan, ya que es para renderizar los datos, asi nos ahorramos repetirla en cada if
    models = {
        'casa': Casa,
        'inquilino': Inquilino,
        'restaurante': Restaurante
    }
    # Obtener el modelo correcto para el tipo de objeto
    if tipo_objeto in models:
        model = models[tipo_objeto]
    else:
        return render(request, 'error.html', {'message': 'Tipo de objeto no válido'})
    # Obtener el objeto
    object = get_object_or_404(model, id=object_id)

    # aunque sea redundante, lo hacemos parfa tener mas constancia de por donde va nuestro codigo
    if request.method == 'POST':
        if tipo_objeto == 'casa':
            casa = get_object_or_404(Casa, id=object_id)
            casa.delete()
            return redirect('admin_casas')
        elif tipo_objeto == 'inquilino':
            # obtenemos el inquilino como metodo para obtener luego el user
            inquilino = get_object_or_404(Inquilino, id=object_id)
            user = inquilino.user
            # al eliminar el user se elimina el inquilino por el delete cascade
            user.delete()
            return redirect('admin_inquilinos')
        elif tipo_objeto == 'restaurante':
            # obtenemos el restaurante como metodo para obtener luego el user
            restaurante = get_object_or_404(Restaurante, id=object_id)
            # al eliminar el user se elimina el inquilino por el delete cascade
            restaurante.delete()
            return redirect('admin_restaurantes')

    return render(request, 'admin/deleteObject.html', {'object': object, 'tipo_objeto': tipo_objeto})


def user_profile_view(request):
    inquilino = get_object_or_404(Inquilino, user=request.user)
    reservas_casas = Reserva.objects.filter(inquilino=inquilino)
    reservas_restaurantes = Reserva_restaurante.objects.filter(
        inquilino=inquilino)

    return render(request, 'userProfile.html', {
        'inquilino': inquilino,
        'reservas_casas': reservas_casas,
        'reservas_restaurantes': reservas_restaurantes,
    })
