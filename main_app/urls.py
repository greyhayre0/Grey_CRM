from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Основные маршруты приложения
    path('', views.dashboard, name='dashboard'),  # Главная страница CRM
    path('statistics/', views.statistics, name='statistics'),  # Страница статистики и аналитики
    path('closed/', views.closed_deals, name='closed_deals'),  # Закрытые и отмененные сделки
    path('successful/', views.successful_deals, name='successful_deals'),  # Успешные сделки
    path('services/', views.services, name='services'),  # Управление услугами
    path('deal/<int:deal_id>/', views.deal_detail, name='deal_detail'),  # Детали конкретной сделки
    path('deal/create/', views.create_deal, name='create_deal'),  # Создание новой сделки
    path('deal/<int:deal_id>/update_status/', views.update_deal_status, name='update_deal_status'),  # API для изменения статуса сделки
    
    # API endpoints
    path('api/services/', views.create_service_api, name='create_service_api'),  # REST API для создания услуг
    
    # Управление контактами и клиентами
    path('contacts/', views.contacts, name='contacts'),  # Список всех клиентов
    path('client/create/', views.create_client, name='create_client'),  # Создание нового клиента
    path('client/<int:client_id>/', views.client_detail, name='client_detail'),  # Детальная информация о клиенте
    path('client/<int:client_id>/deals/', views.client_deals, name='client_deals'),  # Все сделки конкретного клиента

     # ... другие маршруты ...
    path('api/find_client/', views.find_client_api, name='find_client_api'),
    
    # Аутентификация (закомментировано, но можно раскомментировать когда понадобится)
    # path('accounts/login/', auth_views.LoginView.as_view(template_name='crm/login.html'), name='login'),  # Страница входа
    # path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/crm/'), name='logout'),  # Выход из системы
]