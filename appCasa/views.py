from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from .models import Casa, Conversacion, Inquilino, Mensaje, Reserva, Reserva_restaurante, Restaurante
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.utils import timezone


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
    

# funcion que valora si hay una reserva que ya se solape con la que se va a crear    
def reserva_disponible(casa_id, fecha_entrada, fecha_salida):
    # delvovera false(true con negacion) si la reesrva que se qwuiere hacxer esta en el rango de una ya creada completa o parcialmente
    # devolvera true(false con negacion) si no se solapa niguna reserva ya creada con la nueva
    return not Reserva.objects.filter(
        casa_id = casa_id,
        cancelada = False,
        fecha_salida__gte = fecha_entrada,
        fecha_entrada__lte = fecha_salida
    ).exists()

@login_required
def reserve_view(request, casa_id):
    if request.method == 'POST':
        
        fecha_entrada = request.POST.get('fecha_entrada')
        fecha_salida = request.POST.get('fecha_salida')
        num_inquilinos = request.POST.get('num_inquilinos')
        num_menores = request.POST.get('num_menores')
            
        
        if reserva_disponible(casa_id, fecha_entrada, fecha_salida):
            request.session['reservation_data'] = {
                'fecha_entrada': fecha_entrada,
                'fecha_salida': fecha_salida,
                'num_inquilinos': num_inquilinos,
                'casa_id': casa_id
            }
            return render(request, 'payment.html')
        else:
            return render(request, 'error.html')
    
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


def admin_reservas_view(request):
    casa_id = request.GET.get('casa_id')
    inquilino_id = request.GET.get('inquilino_id')
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    
    years = range(2022, 2025)

    # Lista de meses
    months = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]
    
    base_query = Reserva.objects.all()

    # Aplicar filtro por casa si casa_id está presente.
    if casa_id:
        base_query = base_query.filter(casa__id=casa_id)
    # Aplicar filtro por inquilino si inquilino_id está presente.
    if inquilino_id:
        base_query = base_query.filter(inquilino__id=inquilino_id)
    if selected_year:
        base_query = base_query.filter(fecha_entrada__year = selected_year)
    if selected_month:
        base_query = base_query.filter(fecha_entrada__month=selected_month)

    # Ahora aplicamos las condiciones de estado sobre la consulta filtrada.
    reservas = base_query.filter(cancelada=False)
    reservas_canceladas = base_query.filter(cancelada=True)
    reservas_pasadas = base_query.filter(fecha_salida__lt=timezone.now())
    reservas_futuras = base_query.filter(fecha_entrada__gt=timezone.now())

    return render(request, 'admin/adminReservas.html', {
        'reservas': reservas,
        'reservas_canceladas': reservas_canceladas,
        'reservas_pasadas': reservas_pasadas,
        'reservas_futuras': reservas_futuras,
        'casas': Casa.objects.all(),
        'inquilinos': Inquilino.objects.all(),
        'casa_id': casa_id,
        'inquilino_id': inquilino_id,
        'years': years,
        'selected_year': selected_year,
        'months': months,
        'selected_month': selected_month
    })
    
# admin view reservas restaurantes


@user_passes_test(check_is_superuser)
def admin_reservas_restaurantes_view(request):
    reservas = Reserva_restaurante.objects.all()
    return render(request, 'admin/adminReservasRestaurantes.html', {'reservas': reservas})

# Vista CUD


@user_passes_test(check_is_superuser)
def create_object_view(request, tipo_objeto):
    casas = Casa.objects.all()
    inquilinos = Inquilino.objects.all()

    if request.method == 'POST':
        if tipo_objeto == 'casa':
            nombre = request.POST.get('nombre')
            direccion = request.POST.get('direccion')
            licencia = request.POST.get('licencia')
            descripcion = request.POST.get('descripcion')
            num_habitaciones = request.POST.get('num_habitaciones')
            max_inquilinos = request.POST.get('max_inquilinos')
            img_url = request.POST.get('img_url')
            url_name = request.POST.get('url_name')

            # Preparamos el diccionario básico con datos obligatorios
            casa_data = {
                "licencia": licencia,
                "nombre": nombre,
                "direccion": direccion,
                "descripcion": descripcion,
                "numero_habitaciones": num_habitaciones,
                "max_inquilinos": max_inquilinos,
                "img_url": img_url,
                "url_name": url_name
            }
            
            # Añadir precio_noche_persona solo si está presente en el formulario
            precio_noche_persona = request.POST.get('precio_noche_persona')
            if precio_noche_persona:
                casa_data["precio_noche_persona"] = precio_noche_persona

            # Añadir dias_cancel solo si está presente en el formulario
            dias_cancel = request.POST.get('dias_cancel')
            if dias_cancel:
                casa_data["dias_cancel"] = dias_cancel

            # Crear la casa con los datos recopilados
            Casa.objects.create(**casa_data)
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
            img_url = request.POST.get('img_url')
            url_name = request.POST.get('url_name')
            Restaurante.objects.create(numero_licencia=numero_licencia, nombre=nombre,
                                       direccion=direccion, descripcion=descripcion, precio_medio=precio_medio,
                                       img_url=img_url, url_name=url_name)
            return redirect('admin_restaurantes')

        elif tipo_objeto == 'reserva':
            casa_id = request.POST.get('casa')
            inquilino_id = request.POST.get('inquilino')
            fecha_entrada = request.POST.get('fecha_entrada')
            fecha_salida = request.POST.get('fecha_salida')
            num_inquilinos = request.POST.get('num_inquilinos')
            precio_total = request.POST.get('precio_total')

            # Creamos un diccionario para los datos de la reserva
            reserva_data = {
                "casa_id": casa_id,
                "inquilino_id": inquilino_id,
                "fecha_entrada": fecha_entrada,
                "fecha_salida": fecha_salida,
                "num_inquilinos": num_inquilinos,
                "precio_total": precio_total
            }

            # Añadir num_menores solo si está presente en el formulario
            num_menores = request.POST.get('num_menores')
            if num_menores != '':
                reserva_data["num_menores"] = num_menores

            # Añadir cancelada solo si está marcada en el formulario
            cancelada = request.POST.get('cancelada')
            if cancelada == 'on':
                reserva_data["cancelada"] = True
            else:
                reserva_data["cancelada"] = False  # Esto es opcional, depende de si quieres explícitamente establecer False o no

            # Crear la reserva con los datos recopilados
            reserva = Reserva.objects.create(**reserva_data)
            return redirect('admin_reservas')
        
    return render(request, 'admin/createObject.html', {'tipo_objeto': tipo_objeto, 'casas': casas, 'inquilinos': inquilinos})


@user_passes_test(check_is_superuser)
def update_object_view(request, tipo_objeto, object_id):
    # Esta parte sera la misma ara todos los objetods que vegan, ya que es para renderizar los datos, asi nos ahorramos repetirla en cada if
    models = {
        'casa': Casa,
        'inquilino': Inquilino,
        'restaurante': Restaurante,
        'reserva': Reserva
        
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
            casa.precio_noche_persona = request.POST.get('precio_noche_persona')
            casa.img_url = request.POST.get('img_url')
            casa.url_name = request.POST.get('url_name')
            casa.dias_cancel = request.POST.get('dias_cancel')
            casa.save()
            
            return redirect('admin_casas')
        
        
        
        elif tipo_objeto == 'inquilino':
            inquilino = get_object_or_404(Inquilino, id=object_id)
            user = inquilino.user
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')

            nueva_contraseña = request.POST.get('password')
            if nueva_contraseña:
                user.set_password(nueva_contraseña)

            user.save()
            
            inquilino.dni = request.POST.get('dni')
            inquilino.address = request.POST.get('address')
            inquilino.save()
            
            return redirect('admin_inquilinos')
        
        
        
        elif tipo_objeto == 'restaurante':
            restaurante = get_object_or_404(Restaurante, id=object_id)
            restaurante.numero_licencia = request.POST.get('num_licencia')
            restaurante.nombre = request.POST.get('nombre')
            restaurante.direccion = request.POST.get('direccion')
            restaurante.descripcion = request.POST.get('descripcion')
            restaurante.precio_medio = request.POST.get('precio_medio')
            restaurante.img_url = request.POST.get('img_url')
            restaurante.url_name = request.POST.get('url_name')
            restaurante.save()
            
            return redirect('admin_restaurantes')
        
        
        elif tipo_objeto == 'reserva':
            reserva = get_object_or_404(Reserva, id=object_id)
            reserva.fecha_entrada = request.POST.get('fecha_entrada')
            reserva.fecha_salida = request.POST.get('fecha_salida')
            reserva.num_inquilinos = request.POST.get('num_inquilinos')
            reserva.num_menores = request.POST.get('num_menores')
            reserva.precio_total = request.POST.get('precio_total')
            reserva.cancelada = request.POST.get('cancelada')
            reserva.save()
            return redirect('admin_reservas')

    return render(request, 'admin/updateObject.html', {'object': object, 'tipo_objeto': tipo_objeto})


@user_passes_test(check_is_superuser)
def delete_object_view(request, tipo_objeto, object_id):
    # Esta parte sera la misma para todos los objetods que vegan, ya que es para renderizar los datos, asi nos ahorramos repetirla en cada if
    models = {
        'casa': Casa,
        'inquilino': Inquilino,
        'restaurante': Restaurante,
        'reserva': Reserva
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
        
        
        elif tipo_objeto == 'reserva':
            reserva = get_object_or_404(Reserva, id = object_id)
            reserva.cancelada = True
            reserva.save()
            return redirect('admin_reservas')
        
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



# Mensajes 

@login_required
def lista_conversaciones_view(request):
    # Suponiendo que el usuario está involucrado en 'conversaciones'
    conversaciones = request.user.conversaciones.all()
    return render(request, 'conversaciones/listaConversaciones.html', {'conversaciones': conversaciones})

@login_required
def ver_conversacion(request, conversacion_id):
    conversacion = Conversacion.objects.get(id=conversacion_id)
    mensajes = conversacion.mensajes.order_by('fecha_hora')
    return render(request, 'conversaciones/verConversacion.html', {'mensajes': mensajes, 'conversacion_id': conversacion_id})

# Enviar mensaje o respuesta
@login_required
def enviar_mensaje(request, conversacion_id):
    if request.method == 'POST':
        texto = request.POST.get('texto')
        autor = request.user
        conversacion = Conversacion.objects.get(id=conversacion_id)
        Mensaje.objects.create(autor=autor, texto=texto, conversacion=conversacion)
        return redirect('ver_conversacion', conversacion_id=conversacion_id)
    return render(request, 'conversaciones/enviarMensaje.html', {'conversacion_id': conversacion_id})


@login_required
def crear_conversacion(request):
    if request.method == 'POST':
        asunto = request.POST.get('asunto')
        texto = request.POST.get('texto')
        conversacion = Conversacion.objects.create(asunto=asunto)

        if request.user.is_superuser:
            # Superusuario crea la conversación
            usuario_id = request.POST.get('usuario_id')  # ID del usuario normal seleccionado por el superusuario
            usuario = User.objects.get(id=usuario_id)
            conversacion.participantes.add(usuario)
            conversacion.participantes.add(request.user)
        else:
            # Usuario normal crea la conversación
            superuser = User.objects.get(is_superuser=True, username='chencho2')
            conversacion.participantes.add(superuser)
            conversacion.participantes.add(request.user)
        
        # Crear el primer mensaje en la conversación
        Mensaje.objects.create(
            autor=request.user,
            conversacion=conversacion,
            texto=texto
        )
        
        return redirect('lista_conversaciones')
    else:
        if request.user.is_superuser:
            usuarios = User.objects.filter(is_superuser=False)
        else:
            usuarios = None
        return render(request, 'conversaciones/crearConversacion.html', {'usuarios': usuarios})

