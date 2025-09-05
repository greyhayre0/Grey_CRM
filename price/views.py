from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import Service


def services(request):
    """Страница управления услугами"""
    search_query = request.GET.get('search', '')

    services = Service.objects.all().select_related('category').annotate(
        usage_count=Count('dealservice')
    ).order_by('category__name', 'name')

    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    context = {
        'services': services,
        'categories': Service.objects.all(),
        'search_query': search_query,
        'total_services': services.count(),
        'active_services_count': services.filter(is_active=True).count(),
        'avg_price': services.aggregate(
            avg_price=Avg('price'))['avg_price'] or 0,
        'popular_services_count': services.filter(usage_count__gt=5).count(),
    }

    return render(request, 'services.html', context)


# API функции для услуг
@csrf_exempt
def create_service_api(request):
    """API для создания услуги"""
    try:
        data = json.loads(request.body)
        service = Service.objects.create(
            name=data.get('name'),
            price=data.get('price', 0),
            description=data.get('description', ''),
            duration_days=data.get('duration_days', 7),
            is_active=data.get('is_active', True)
        )

        return JsonResponse({
            'success': True,
            'service_id': service.id,
            'message': 'Услуга успешно создана'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def service_detail_api(request, service_id):
    """API для работы с конкретной услугой"""
    try:
        service = Service.objects.get(id=service_id)

        if request.method == 'GET':
            return JsonResponse({
                'id': service.id,
                'name': service.name,
                'price': float(service.price),
                'description': service.description,
                'duration_days': service.duration_days,
                'is_active': service.is_active
            })
        elif request.method == 'PUT':
            data = json.loads(request.body)
            service.name = data.get('name',
                                    service.name)
            service.price = data.get('price',
                                     service.price)
            service.description = data.get('description',
                                           service.description)
            service.duration_days = data.get('duration_days',
                                             service.duration_days)
            service.is_active = data.get('is_active',
                                         service.is_active)
            service.save()
            return JsonResponse({'success': True})
        elif request.method == 'DELETE':
            service.delete()
            return JsonResponse({'success': True})

    except Service.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Услуга не найдена'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def toggle_service_api(request, service_id):
    """API для переключения статуса услуги"""
    try:
        service = Service.objects.get(id=service_id)
        service.is_active = not service.is_active
        service.save()

        return JsonResponse({
            'success': True,
            'is_active': service.is_active
        })

    except Service.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Услуга не найдена'
        }, status=404)
