from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Avg
from django.utils.timezone import now
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from .forms import *
from .models import *
import random

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
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
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
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
    recipes = Recipe.objects.filter(author=request.user)
    return render(request, 'recetas/ver_recetas_propias.html', {'recetas':recipes})

def recipe_detail(request, recipe_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    ratings = RecipeRating.objects.filter(recipe=recipe)
    comments = Comment.objects.filter(recipe=recipe)
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    colections = Collection.objects.filter(user=request.user)
    recipe_owner = recipe.author 

    context = {
        'recipe': recipe,
        'ratings': ratings,
        'comments': comments,
        'average_rating': average_rating,
        'colecciones':colections,
        'recipe_owner': recipe_owner,
        'view_name': 'recipe_detail',
    }
    return render(request, 'recetas/receta_detalle.html', context)

def edit_recipe(request, recipe_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            messages.success(request, 'Se Ha Editado Con Exito!')
            return redirect('ver_receta_propia')
    else:
        form = RecipeForm(instance=recipe)

    return render(request, 'recetas/editar_recetas.html', {'form': form, 'recipe': recipe})

def delete_recipe(request, recipe_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    if request.method == 'POST':
        recipe.delete()
        return redirect('ver_receta_propia')  # Redirigir a la lista de recetas después de eliminar

    return render(request, 'delete_recipe.html', {'recipe': recipe})

def rate_recipe(request, recipe_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas Iniciar Sesion Para Esta Acción')
        return redirect('login')
    
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == "POST":
        rating_value = int(request.POST.get('rating'))
        
        # Buscar si el usuario ya ha puntuado esta receta
        rating, created = RecipeRating.objects.get_or_create(user=request.user, recipe=recipe)
        rating.rating = rating_value
        rating.save()

        # Redirigir a la misma página de detalles de la receta
        return redirect('recipe_detail', recipe_id=recipe.id)
    return render(request, 'recetas/receta_detalle.html', {'recipe': recipe})

def add_comment(request, recipe_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == "POST":
        content = request.POST.get('content')

        # Crear un nuevo comentario
        Comment.objects.create(user=request.user, recipe=recipe, content=content)

        # Redirigir a la misma página de detalles de la receta
        return redirect('recipe_detail', recipe_id=recipe.id)
    return render(request, 'recetas/receta_detalle.html', {'recipe': recipe})

def all_recipes(request):
    query = request.GET.get('q')  # Término de búsqueda
    selected_cuisine = request.GET.get('cuisine')  # Cocina seleccionada
    preparation_time = request.GET.get('preparation_time')  # Tiempo de preparación
    publication_date = request.GET.get('publication_date')  # Fecha de publicación

    recipes = Recipe.objects.all()

    if query:
        recipes = recipes.filter(title__icontains=query)

    if selected_cuisine:
        recipes = recipes.filter(cuisine__name=selected_cuisine)

    if preparation_time:
        if preparation_time == "menos30":
            recipes = recipes.filter(preparation_time__lt=30)
        elif preparation_time == "30-60":
            recipes = recipes.filter(preparation_time__gte=30, preparation_time__lte=60)
        elif preparation_time == "mas60":
            recipes = recipes.filter(preparation_time__gt=60)

    if publication_date:
        today = now()
        if publication_date == "ultimo_mes":
            last_month = today - timedelta(days=30)
            recipes = recipes.filter(created_at__gte=last_month)
        elif publication_date == "ultimo_anio":
            last_year = today - timedelta(days=365)
            recipes = recipes.filter(created_at__gte=last_year)
        elif publication_date == "anteriores":
            last_year = today - timedelta(days=365)
            recipes = recipes.filter(created_at__lt=last_year)

    cuisenes = Cuisine.objects.all()

    contexto = {
        'recetas': recipes,
        'cocinas': cuisenes,
    }
    return render(request, 'recetas/ver_recetas.html', contexto)

def create_collection(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.user = request.user
            collection.save()
            messages.success(request, 'Se Ha Creado La Coleccíon Con Exito!')
            return redirect('create_collection') 
    else:
        form = CollectionForm()

    return render(request, 'colecciones/crear_coleccion.html', {'form': form})

def add_recipe_to_collections(request, recipe_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
    if request.method == 'POST':
        collection_ids = request.POST.getlist('collections')

        recipe = get_object_or_404(Recipe, id=recipe_id)
        collections = Collection.objects.filter(id__in=collection_ids, user=request.user)

        for collection in collections:
            if collection.recipes.filter(id=recipe.id).exists():
                # Mostrar mensaje si la receta ya está en la colección
                messages.info(request, f'La receta "{recipe.title}" ya está en la colección "{collection.name}".')
            else:
                # Agregar la receta a la colección si no está ya presente
                collection.recipes.add(recipe)
                messages.success(request, f'Receta "{recipe.title}" añadida a la colección "{collection.name}".')

        return redirect('recipe_detail', recipe_id=recipe_id)
    
def user_collections(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
    collections = Collection.objects.filter(user=request.user)
    return render(request, 'colecciones/lista_colecciones.html', {'collections': collections})

def collection_detail(request, collection_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    recipes = collection.recipes.all()
    return render(request, 'colecciones/detalle_coleccion.html', {'collection': collection, 'recipes': recipes})

def edit_profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        messages.success(request, 'Tu perfil ha sido actualizado.')
        return redirect('edit_profile')

    # Información de seguidores y seguidos
    following_count = Follow.objects.filter(follower=request.user).count()
    followers_count = Follow.objects.filter(following=request.user).count()

    context = {
        'following_count': following_count,
        'followers_count': followers_count,
    }

    return render(request, 'perfil/edit_profile.html', context)

def following_list(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
    following = Follow.objects.filter(follower=request.user)
    return render(request, 'perfil/siguiendo_list.html', {'following': following})

def followers_list(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
    followers = Follow.objects.filter(following=request.user)
    return render(request, 'perfil/seguidos_list.html', {'followers': followers})

def follow_user(request, user_id, recipe_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')

    user_to_follow = get_object_or_404(User, id=user_id)

    # Evitar que un usuario se siga a sí mismo
    if user_to_follow != request.user:
        follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        
        if created:
            # Si la relación fue creada, significa que ahora sigue al usuario
            messages.success(request, f'Ahora sigues a {user_to_follow.first_name}')
        else:
            # Si ya existía la relación, puedes decidir no hacer nada o informar al usuario
            messages.info(request, f'Ya sigues a {user_to_follow.first_name}')

    return redirect('recipe_detail', recipe_id)

def unfollow_user(request, user_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Necesitas iniciar sesión para realizar está acción.')
        return redirect('login')
    follow = get_object_or_404(Follow, follower=request.user, following_id=user_id)
    follow.delete()
    return redirect('following_list')

from django.core.mail import send_mail

def recuperar_contraseña(request):
    if request.method == 'POST':
        correo_user = request.POST['correo']
        codigo_aleatorio = random.randint(1000, 9999)

        # Guardar el código generado en la sesión
        request.session['codigo_aleatorio'] = codigo_aleatorio

        send_mail(
            'Recuperar Contraseña',
            f'No compartas este código con nadie. Tu código es: {codigo_aleatorio}',
            'codenexus791@gmail.com',
            [correo_user],
            fail_silently=False,
        )

        contexto = {
            'correo_usuario': correo_user,
            'mostrar_reenviar': False,  # No mostrar botón de reenviar inicialmente
            'deshabilitar_inputs': False  # Habilitar inputs inicialmente
        }
        return render(request, 'recuperar_contraseña/validacion_codigo.html', contexto)

    return render(request, 'recuperar_contraseña/validacion_codigo.html')


def validar_codigo(request):
    if request.method == 'POST':
        codigo_ingresado = ''.join([
            request.POST['codigo1'],
            request.POST['codigo2'],
            request.POST['codigo3'],
            request.POST['codigo4']
        ])
        codigo_aleatorio = str(request.session.get('codigo_aleatorio'))
        correo_user = request.POST['correo']

        if codigo_ingresado == codigo_aleatorio:
            contexto = {
                'correo':correo_user
            }
            return render(request, 'recuperar_contraseña/formulario_recuperacion.html', contexto)
        else:
            # Código incorrecto, mostrar el botón de reenviar y deshabilitar inputs
            contexto = {
                'correo_usuario': correo_user,
                'mostrar_reenviar': True,
                'deshabilitar_inputs': True
            }
            return render(request, 'recuperar_contraseña/validacion_codigo.html', contexto)

    return redirect('recuperar_contraseña')
    
def cambio_contraseña(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        nueva_contraseña = request.POST.get('new_password')
        confirmar_contraseña = request.POST.get('confirm_password')

        if nueva_contraseña != confirmar_contraseña:
            messages.error(request, 'Las contraseñas no coinciden. Por favor, inténtalo de nuevo.')
            return render(request, 'recuperar_contraseña/formulario_recuperacion.html', {'correo': correo})

        try:
            usuario = User.objects.get(email=correo)
            usuario.password = make_password(nueva_contraseña)
            usuario.save()
            messages.success(request, 'Tu contraseña ha sido actualizada exitosamente.')
            return redirect('login') 
        except User.DoesNotExist:
            messages.error(request, 'No se encontró ningún usuario con el correo proporcionado al inicio.')
            return render(request, 'recuperar_contraseña/formulario_recuperacion.html', {'correo': correo})

    return redirect('login')