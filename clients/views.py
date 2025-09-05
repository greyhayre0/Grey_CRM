from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from .models import Client


def client_detail(request, client_id):
    """Детальная страница клиента"""
    client = get_object_or_404(
        Client.objects.prefetch_related(
            'deals__services', 'deals__dealservice_set'),
        id=client_id
    )

    deals = client.deals.all().select_related('client').prefetch_related(
        'services', 'dealservice_set'
    ).order_by('-created_at')

    context = {
        'client': client,
        'deals': deals,
        'total_deals': deals.count(),
        'total_spent': sum(
            deal.total_price for deal in deals if deal.status
            in ['completed', 'successful']),
        'active_deals': deals.exclude(
            status__in=['completed', 'cancelled', 'successful', 'closed']
            ).count(),
    }

    return render(request, 'client_detail.html', context)


def client_deals(request, client_id):
    """Страница со сделками клиента"""
    client = get_object_or_404(Client, id=client_id)

    deals = client.deals.all().select_related('client').prefetch_related(
        'services', 'dealservice_set'
    ).order_by('-created_at')

    context = {
        'client': client,
        'deals': deals,
    }
    return render(request, 'client_deals.html', context)


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


def contacts(request):
    """Страница контактов"""
    clients = Client.objects.all().order_by('name')
    return render(request, 'contacts.html', {'clients': clients})


def create_client(request):
    """Создание нового клиента"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            notes = request.POST.get('notes')

            client = Client.objects.create(
                name=name,
                phone=phone,
                email=email,
                notes=notes or ''
            )

            return redirect('contacts')

        except Exception as e:
            return JsonResponse({
                'success': False,
                'errors': {'general': f'Ошибка при создании клиента: {str(e)}'}
            }, status=400)

    return JsonResponse({
        'success': False,
        'errors': {'general': 'Неверный метод запроса'}
    }, status=405)
