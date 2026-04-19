from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.turmas, name='turmas'),
    path('analises/', views.analises, name='analises'),
    path('chamada/<int:pk>/', views.realizar_chamada, name='chamada'),
    path('cadastroAluno/', views.cadastroAluno, name='cadastroAluno'),
    path('cadastroTurma/', views.cadastroTurma, name='cadastroTurma'),
    path('controle/', views.controle, name='controle'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]