from django.urls import path
from . import views

urlpatterns = [
    path('', views.turmas, name='turmas'),
    path('login/', views.login_view, name='login'),
    path('chamada/<int:pk>/', views.realizar_chamada, name='chamada'),
    path('analises/', views.analises, name='analises'),
    path('cadastros/', views.cadastros, name='cadastros'),
    # Se houver uma rota de logout, adicione name='logout' também
]