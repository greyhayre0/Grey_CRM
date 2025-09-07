from django.http import JsonResponse
from django.db.models import Q
from clients.models import Client
from price.models import Service
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json


def find_client_api(request):
    """API для поиска клиента по телефону"""
    phone = request.GET.get('phone', '').strip()

    if not phone:
        return JsonResponse({'success': False, 'message': 'Не указан телефон'})

    try:
        # Ищем клиента по точному совпадению телефона
        client = Client.objects.filter(
            Q(phone=phone) | Q(phone__contains=phone)
        ).first()

        if client:
            return JsonResponse({
                'success': True,
                'client': {
                    'id': client.id,
                    'name': client.name,
                    'phone': client.phone,
                    'email': client.email or ''
                }
            })
        else:
            return JsonResponse(
                {'success': False, 'message': 'Клиент не найден'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


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

''' Пока ненужно не работает
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
'''