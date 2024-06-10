from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('index/', views.index_view, name="index"),
    path('register/', views.register_view, name="register"),
    path('log_out/', views.logOut_view, name='log_out'),
    path('contact/', views.contact_view, name='contact'),
    path('success/', views.success_view, name='success'),
    path('error/', views.error_view, name='error'),
    path('payment/', views.payment_view, name='payment'),
    
    # casas
    path('api_reservas/<int:casa_id>/', views.api_reservas, name='api_reservas'),
    path('reserve/<int:casa_id>/', views.reserve_view, name='reserve'),
    path('casaRio/', views.casa_rio_view, name='casaRio'),
    path('casaLuisa/', views.casa_luisa_view, name='casaLuisa'),
    path('casaPaco/', views.casa_paco_view, name='casaPaco'),
    path('casas_panel/', views.casas_panel, name='casas_panel'),
    
    
    
    # restaurantes
    path('restaurant/', views.restaurant_view, name='restaurant'),
    path('api_restaurante/<str:restaurante_licencia>/', views.api_restaurante, name='api_restaurante'),
    path('barPaco/', views.bar_paco_view, name='barPaco'),
    path('barLoscanillas/', views.bar_loscanillas_view, name='barLoscanillas'),
    path('reserve_restaurante/<str:restaurante_licencia>/', views.reserva_restaurante, name='reserva_restaurante'),
    
    # vista administrador
    path('admin_panel/', views.admin_panel_view, name='admin_panel'),
    path('admin_panel/casas/', views.admin_casas_view, name='admin_casas'),
    path('admin_panel/inquilinos/', views.admin_inquilino_view, name='admin_inquilinos'),
    path('admin_panel/restaurantes/', views.admin_restaurantes_view, name='admin_restaurantes'),
    path('admin_panel/reservas/', views.admin_reservas_view, name='admin_reservas'),
    path('admin_panel/reservasRestaurantes/', views.admin_reservas_restaurantes_view, name='admin_reservas_restaurantes'),
    path('admin_panel/create/<str:tipo_objeto>', views.create_object_view, name='create_object'),
    path('admin_panel/update/<int:object_id>/<str:tipo_objeto>', views.update_object_view, name='update_object'),
    path('admin_panel/delete/<int:object_id>/<str:tipo_objeto>', views.delete_object_view, name='delete_object'),
    
    # vista perfil usuario
    path('user_profile/', views.user_profile_view, name='user_profile'),
    
    
    # vista conversaciones
    path('lista_conversaciones/', views.lista_conversaciones_view, name='lista_conversaciones'),
    path('ver_conversacion/<int:conversacion_id>/', views.ver_conversacion, name='ver_conversacion'),
    path('enviar_mensaje/<int:conversacion_id>/', views.enviar_mensaje, name='enviar_mensaje'),
    path('crear_conversacion', views.crear_conversacion, name='crear_conversacion'),

    
]
