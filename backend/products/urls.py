from django.urls import path,include
from . import views
from rest_framework import DefaultRouter

router=DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)

urlpatterns=[
    path('', include(router.urls)), 

]



