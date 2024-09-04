from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="index"),
    path('registrarse/', registrarse, name="registrarse"),
    path('registro_usuario/', register_user, name="registro_usuario"),
    path('login/', login_view, name="login"),
    path('cerrar_sesion/', cerrar_sesion, name="cerrar_sesion"),
    path('crear_receta/', create_recipe, name="crear_receta"),
    path('ver_receta_propia/', ver_recetas_propias, name="ver_receta_propia"),
]