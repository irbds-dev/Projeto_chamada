from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.turmas, name='turmas'),
    path('login/', views.login_view, name='login'),
    path('chamada/<int:pk>/', views.realizar_chamada, name='chamada'),
    path('analises/', views.analises, name='analises'),
    path('cadastroAluno/', views.cadastroAluno, name='cadastroAluno'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]