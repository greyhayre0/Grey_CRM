from django.shortcuts import render
from django.db.models import Q, Count, Avg

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
