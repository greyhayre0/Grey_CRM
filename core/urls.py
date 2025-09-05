from django.urls import path
from clients.views import contacts, create_client, client_detail, client_deals, find_client_api
from deals.views import dashboard, closed_deals, successful_deals, deal_detail, create_deal, update_deal_status
from statistic.views import statistics
from price.views import services, create_service_api

urlpatterns = [
    # Основные маршруты приложения
    path('', dashboard,
         name='dashboard'),  # Главная страница
    path('statistics/', statistics,
         name='statistics'),
    path('closed/', closed_deals,
         name='closed_deals'),
    path('successful/', successful_deals,
         name='successful_deals'),
    path('services/', services,
         name='services'),
    path('deal/<int:deal_id>/', deal_detail,
         name='deal_detail'),
    path('deal/create/', create_deal,
         name='create_deal'),
    path('deal/<int:deal_id>/update_status/', update_deal_status,
         name='update_deal_status'),

    # API endpoints
    path('api/services/', create_service_api,
         name='create_service_api'),

    # Управление контактами и клиентами
    path('contacts/', contacts,
         name='contacts'),
    path('client/create/', create_client,
         name='create_client'),
    path('client/<int:client_id>/', client_detail,
         name='client_detail'),
    path('client/<int:client_id>/deals/', client_deals,
         name='client_deals'),

    # ... другие маршруты ...
    path('api/find_client/', find_client_api,
         name='find_client_api'),
]
