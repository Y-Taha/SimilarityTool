from django.urls import path
from . import views

urlpatterns = [
    #path('', views.home,name='tune-home'),
    path('', views.upload, name='tune-upload'),
    path('show/',views.show,name='tune-show')
]