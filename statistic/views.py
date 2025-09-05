from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from deals.models import Deal, DealService
from clients.models import Client
from price.models import Service


def statistics(request):
    """Страница статистики"""
    # Получение данных из БД
    total_revenue = DealService.objects.aggregate(
        Sum('price'))['price__sum'] or Decimal('0')
    total_deals = Deal.objects.count()

    # Статистика по услугам
    service_stats = Service.objects.annotate(
        count=Count('dealservice'),
        total_revenue=Sum('dealservice__price'),
        avg_price=Avg('dealservice__price')
    ).filter(count__gt=0)

    # Данные для графиков
    monthly_data = [120, 190, 150, 170, 220, 190, 240, 170, 200, 180, 160, 220]
    monthly_labels = ['Янв', 'Фев', 'Мар', 'Апр', 'Май',
                      'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

    # Дополнительная статистика
    completed_deals = Deal.objects.filter(status='completed').count()
    successful_deals = Deal.objects.filter(status='successful').count()
    total_completed = completed_deals + successful_deals

    # Функция для преобразования Decimal в float
    def decimal_to_float(value):
        if isinstance(value, Decimal):
            return float(value)
        return value

    # Подготавливаем данные для графиков
    services_revenue = []
    for stats in service_stats[:6]:
        if stats.total_revenue is not None:
            services_revenue.append(float(stats.total_revenue))
        else:
            services_revenue.append(0.0)

    context = {
        'total_revenue': decimal_to_float(total_revenue),
        'total_deals': total_deals,
        'total_completed': total_completed,
        'completed_deals': completed_deals,
        'successful_deals': successful_deals,
        'new_clients': Client.objects.filter(
            created_at__gte=timezone.now()-timedelta(days=30)).count(
            ),
        'conversion_rate': round(
            (total_completed / total_deals * 100) if total_deals > 0 else 0, 1
            ),
        'revenue_change': 15.2,
        'deals_change': 8.7,
        'clients_change': 12.3,
        'conversion_change': 3.2,
        'service_stats': service_stats,
        'monthly_data': json.dumps(monthly_data),
        'monthly_labels': json.dumps(monthly_labels),
        'services_data': json.dumps(services_revenue),
        'services_labels': json.dumps(
            [stats.name for stats in service_stats[:6]]
            ),
    }

    return render(request, 'statistics.html', context)


def update_statistics(request):
    """Обновление статистики (AJAX)"""
    period = request.GET.get('period', 'month')
    return JsonResponse({
        'monthly_labels': ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн'],
        'monthly_data': [120, 190, 150, 170, 220, 190],
        'services_labels': ['Услуга 1', 'Услуга 2', 'Услуга 3'],
        'services_data': [40, 30, 30]
    })
