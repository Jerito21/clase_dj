from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('add_product/', views.add_product, name='add_product'),
    path('delete_product/<int:pk>/', views.delete_product, name='delete_product'),
]