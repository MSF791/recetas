from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RecipeForm
from .models import *

def index(request):
    return render(request, 'index.html',)

def registrarse(request):
    return render(request, 'registrarse.html')

def register_user(request):
    if request.method == 'POST':
        nombres = request.POST['nombres']
        apellidos = request.POST['apellidos']
        email = request.POST['email']
        password = request.POST['pass']
        
        # Verificar si el correo ya existe
        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está en uso.")
            return redirect('registrarse')  # Redirige de nuevo al formulario

        # Crear el nuevo usuario
        user = User.objects.create_user(
            username=email,  # Puedes usar el correo como nombre de usuario
            email=email,
            password=password,
            first_name=nombres,
            last_name=apellidos
        )
        
        messages.success(request, "Usuario registrado con éxito.")
        return redirect('registrarse')  
    else:
        return render(request, 'registrarse.html')
    
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # Autenticar el usuario
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Has Iniciado Sesion Con Exito")
            return redirect('login')  # Redirige al home o a la página que desees
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
            return redirect('login')
    return render(request, 'login.html')

def cerrar_sesion(request):
    logout(request)
    messages.success(request, 'Has Cerrado La Sesion Exitosamente')
    return render(request, 'login.html')

def create_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user  # Asignar el autor actual
            recipe.save()
            messages.success(request, 'Receta Creada Con Exito!')  # Redirigir a la vista de detalles de la receta
            redirect('crear_receta')
    else:
        form = RecipeForm()
    return render(request, 'recetas/crear_receta.html', {'form': form})

def ver_recetas_propias(request):
    recipes = Recipe.objects.filter(author=request.user)
    return render(request, 'recetas/ver_recetas_propias.html', {'recetas':recipes})