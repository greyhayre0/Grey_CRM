from django.urls import path
from . import views

urlpatterns = [
    # Основные маршруты приложения
    path('', views.dashboard,
         name='dashboard'),  # Главная страница
    path('statistics/', views.statistics,
         name='statistics'),
    path('closed/', views.closed_deals,
         name='closed_deals'),
    path('successful/', views.successful_deals,
         name='successful_deals'),
    path('services/', views.services,
         name='services'),
    path('deal/<int:deal_id>/', views.deal_detail,
         name='deal_detail'),
    path('deal/create/', views.create_deal,
         name='create_deal'),
    path('deal/<int:deal_id>/update_status/', views.update_deal_status,
         name='update_deal_status'),

    # API endpoints
    path('api/services/', views.create_service_api,
         name='create_service_api'),

    # Управление контактами и клиентами
    path('contacts/', views.contacts,
         name='contacts'),
    path('client/create/', views.create_client,
         name='create_client'),
    path('client/<int:client_id>/', views.client_detail,
         name='client_detail'),
    path('client/<int:client_id>/deals/', views.client_deals,
         name='client_deals'),

    # ... другие маршруты ...
    path('api/find_client/', views.find_client_api,
         name='find_client_api'),
]
