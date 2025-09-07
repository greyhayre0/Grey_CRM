from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import timedelta
from decimal import Decimal
import json

from deals.models import Deal, DealService
from clients.models import Client
from price.models import Service
from core.forms import CommentForm


def dashboard(request):
    """Главная страница с группировкой сделок по статусам"""
    # Активные услуги
    services = Service.objects.filter(is_active=True)
    clients = Client.objects.all().order_by('name')

    # Сделки с предзагрузкой связанных данных
    deals_new = Deal.objects.filter(
        status='new').select_related(
            'client').prefetch_related('services')
    deals_in_progress = Deal.objects.filter(
        status='in_progress').select_related(
            'client').prefetch_related('services')
    deals_ready = Deal.objects.filter(
        status='ready').select_related(
            'client').prefetch_related('services')
    deals_completed = Deal.objects.filter(
        status='completed').select_related(
            'client').prefetch_related('services')
    deals_cancelled = Deal.objects.filter(
        status='cancelled').select_related(
            'client').prefetch_related('services')

    # Статистика по статусам
    deals_by_status = Deal.objects.values('status').annotate(count=Count('id'))
    status_counts = {status: count for status, count in deals_by_status}

    # Просроченные сделки (не завершенные и дата окончания прошла)
    expired_deals = Deal.objects.filter(
        Q(status__in=['new', 'in_progress', 'ready']) &
        Q(end_date__lt=timezone.now())
    ).select_related('client').prefetch_related('services')

    # Общая статистика
    total_deals = Deal.objects.count()
    total_revenue = DealService.objects.aggregate(
        total=Sum('price'))['total'] or 0

    # Статистика по услугам
    popular_services = Service.objects.annotate(
        deal_count=Count('dealservice')
    ).order_by('-deal_count')[:5]

    context = {
        'deals_new': deals_new,
        'deals_in_progress': deals_in_progress,
        'deals_ready': deals_ready,
        'deals_completed': deals_completed,
        'deals_cancelled': deals_cancelled,
        'expired_deals': expired_deals,
        'status_counts': status_counts,
        'services': services,
        'total_deals': total_deals,
        'total_revenue': total_revenue,
        'popular_services': popular_services,
        'clients': clients,
    }
    return render(request, 'dashboard.html', context)


def all_deals(request):
    # Получаем все сделки
    deals = Deal.objects.select_related('client').all()

    # Фильтрация по статусу
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        deals = deals.filter(status=status_filter)

    # Фильтрация по дате
    date_filter = request.GET.get('date', 'all')
    if date_filter != 'all':
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        if date_filter == 'today':
            deals = deals.filter(created_at__date=now.date())
        elif date_filter == 'week':
            week_ago = now - timedelta(days=7)
            deals = deals.filter(created_at__gte=week_ago)
        elif date_filter == 'month':
            month_ago = now - timedelta(days=30)
            deals = deals.filter(created_at__gte=month_ago)
        elif date_filter == 'quarter':
            quarter_ago = now - timedelta(days=90)
            deals = deals.filter(created_at__gte=quarter_ago)

    # Сортировка
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'oldest':
        deals = deals.order_by('created_at')
    elif sort_by == 'price_high':
        deals = deals.order_by('-price')
    elif sort_by == 'price_low':
        deals = deals.order_by('price')
    else:  # newest по умолчанию
        deals = deals.order_by('-created_at')

    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        deals = deals.filter(
            Q(client__name__icontains=search_query) |
            Q(client__phone__icontains=search_query) |
            Q(services__icontains=search_query)
        )

    # Пагинация
    paginator = Paginator(deals, 25)  # 25 сделок на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'deals': page_obj,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'sort_by': sort_by,
        'search_query': search_query,
    }

    return render(request, 'closed.html', context)


def deal_detail(request, deal_id):
    """Детальная страница сделки"""
    deal = get_object_or_404(
        Deal.objects.select_related('client').prefetch_related(
                       'services', 'comments__author', 'dealservice_set'
                       ),
        id=deal_id
    )

    services_with_prices = deal.dealservice_set.select_related('service').all()
    comment_form = CommentForm()

    if request.method == 'POST':
        if 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.deal = deal
                comment.author = request.user
                comment.save()
                messages.success(request, 'Комментарий добавлен')
                return redirect('deal_detail', deal_id=deal.id)

    context = {
        'deal': deal,
        'services_with_prices': services_with_prices,
        'comment_form': comment_form,
    }
    return render(request, 'deal_detail.html', context)


@csrf_exempt
@csrf_exempt
def create_deal(request):
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            client_name = request.POST.get('client_name')
            client_phone = request.POST.get('client_phone')
            service_ids = request.POST.getlist('services[]')
            prices = request.POST.getlist('prices[]')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            status = request.POST.get('status')
            description = request.POST.get('description')

            # Валидация обязательных полей
            if not all(
                [client_name, client_phone, start_date, end_date, status]
            ):
                return JsonResponse({
                    'success': False,
                    'errors': {
                        'general': 'Все обязательные поля'
                        'должны быть заполнены'
                        }
                }, status=400)

            if not service_ids or not any(service_ids):
                return JsonResponse({
                    'success': False,
                    'errors': {'services': 'Выберите хотя бы одну услугу'}
                }, status=400)

            # Создаем или находим клиента
            client, created = Client.objects.get_or_create(
                phone=client_phone,
                defaults={'name': client_name}
            )

            # Если клиент уже существовал, но имя изменилось - обновляем
            if not created and client.name != client_name:
                client.name = client_name
                client.save()

            # Преобразуем даты с учетом timezone
            from django.utils import timezone
            import datetime

            # Преобразуем строки в datetime объекты
            start_date_obj = datetime.datetime.fromisoformat(
                start_date.replace('Z', '+00:00'))
            end_date_obj = datetime.datetime.fromisoformat(
                end_date.replace('Z', '+00:00'))

            # Делаем даты aware (с учетом timezone)
            start_date_aware = timezone.make_aware(start_date_obj)
            end_date_aware = timezone.make_aware(end_date_obj)

            # Создаем сделку
            deal = Deal.objects.create(
                client=client,
                description=description or '',
                status=status,
                start_date=start_date_aware,
                end_date=end_date_aware
            )

            # Добавляем услуги к сделке
            for i in range(len(service_ids)):
                if service_ids[i]:  # Проверяем, что услуга выбрана
                    service = Service.objects.get(id=service_ids[i])
                    price = prices[i] if i < len(prices) else service.price

                    # Создаем связь между сделкой и услугой
                    DealService.objects.create(
                        deal=deal,
                        service=service,
                        price=price or service.price
                        )

            return redirect('dashboard')

        except Service.DoesNotExist as e:
            print(f"DEBUG: Service error - {str(e)}")
            return JsonResponse({
                'success': False,
                'errors': {'service': 'Услуга не найдена'}
            }, status=400)
        except Exception as e:
            print(f"DEBUG: General error - {str(e)}")
            return JsonResponse({
                'success': False,
                'errors': {'general': f'Ошибка при создании сделки: {str(e)}'}
            }, status=400)

    return JsonResponse({
        'success': False,
        'errors': {'general': 'Неверный метод запроса'}
    }, status=405)


@csrf_exempt
@require_POST
def update_deal_status(request, deal_id):
    """API для обновления статуса сделки"""
    try:
        deal = get_object_or_404(Deal, id=deal_id)

        if request.content_type == 'application/json':
            data = json.loads(request.body)
            new_status = data.get('status')
        else:
            new_status = request.POST.get('status')

        if new_status not in dict(Deal.STATUS_CHOICES).keys():
            return JsonResponse({
                'success': False,
                'message': 'Неверный статус',
                'valid_statuses': list(dict(Deal.STATUS_CHOICES).keys())
            }, status=400)

        old_status = deal.status
        deal.status = new_status
        deal.save()

        return JsonResponse({
            'success': True,
            'message': 'Статус успешно обновлен',
            'new_status': new_status,
            'status_display': dict(Deal.STATUS_CHOICES)[new_status],
            'deal_id': deal_id
        })

    except Deal.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Сделка не найдена'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Неверный формат JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка сервера: {str(e)}'
        }, status=500)


# Вспомогательные функции
def restore_deal(request, deal_id):
    """Восстановление сделки"""
    if request.method == 'POST':
        try:
            deal = Deal.objects.get(
                id=deal_id, status__in=['completed', 'cancelled'])
            deal.status = 'new'
            deal.save()
            return JsonResponse({'success': True})
        except Deal.DoesNotExist:
            return JsonResponse(
                {'success': False, 'error': 'Сделка не найдена'})
    return JsonResponse(
        {'success': False, 'error': 'Неверный метод запроса'})


def delete_deal(request, deal_id):
    """Удаление сделки"""
    if request.method == 'POST':
        try:
            deal = Deal.objects.get(id=deal_id)
            deal.delete()
            messages.success(request, 'Сделка успешно удалена')
            return redirect('closed_deals')  # или на другую страницу
        except Deal.DoesNotExist:
            messages.error(request, 'Сделка не найдена')
            return redirect('closed_deals')
    
    # Если метод не POST
    messages.error(request, 'Неверный метод запроса')
    return redirect('closed_deals')
