from django.urls import path,include
from .views import *
urlpatterns = [
    path('register/',register,name='register'),
    path('login/',login_view,name='login'),
    path('logout/',logout_view,name='logout'),
    path('',home,name='home'),
    path('profile/',profile,name='profile'),
    path('product/add/', add_product, name='add_product'),
    path('product/<int:product_id>/edit/', edit_product, name='edit_product'),
    path('product/<int:product_id>/delete/', delete_product, name='delete_product'),
    path('product/<int:product_id>/detail/', product_detail, name='product_detail'),
]
