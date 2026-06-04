from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('turmas', views.turmas, name='turmas'),
    path('analises/', views.analises, name='analises'),
    path('analises/dados/', views.dados_dashboard, name='dados_dashboard'),
    path('chamada/<int:id_turma>/', views.realizar_chamada, name='chamada'),
    path('cadastroAluno/', views.cadastroAluno, name='cadastroAluno'),
    path('cadastroTurma/', views.cadastroTurma, name='cadastroTurma'),
    path('chamada/editar/', views.editarChamada, name='editarChamada'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]