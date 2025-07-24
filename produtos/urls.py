# produtos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_produtos, name='lista_produtos'),
    path('produto/<int:pk>/', views.detalhe_produto, name='detalhe_produto'),
    path('produto/novo/', views.criar_produto, name='criar_produto'),
    path('produto/<int:pk>/editar/', views.editar_produto, name='editar_produto'),
    path('produto/<int:pk>/deletar/', views.deletar_produto, name='deletar_produto'),
    path('categoria/nova/', views.criar_categoria, name='criar_categoria'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('produto/<int:pk>/movimentar/', views.movimentar_estoque, name='movimentar_estoque'), # <--- URL para a movimentação
    #path('relatorios/em_falta/', views.relatorio_produtos_em_falta, name='relatorio_produtos_em_falta'),

]