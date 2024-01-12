from django.urls import path
from . import views

app_name = 'polling'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:poll_id>/', views.detail, name='detail'),
    path('<int:poll_id>/results_api/', views.poll_results_api, name='poll_results_api'),

]
