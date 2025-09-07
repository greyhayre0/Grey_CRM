from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Deal(models.Model):
    """Модель сделки с клиентом"""
    STATUS_CHOICES = [
        ('new', 'Принята'),
        ('in_progress', 'В работе'),
        ('ready', 'Готов к выдаче'),
        ('successful', 'Успешная'),
        ('closed', 'Закрытая'),
    ]

    # Используем строковую ссылку вместо импорта
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        verbose_name="Клиент",
        related_name='deals'
    )
    services = models.ManyToManyField(
        'price.Service',  # Используем строковую ссылку
        through='DealService',
        verbose_name="Услуги"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='new', verbose_name="Статус")
    start_date = models.DateTimeField(verbose_name="Дата начала")
    end_date = models.DateTimeField(verbose_name="Дата окончания")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Сделка"
        verbose_name_plural = "Сделки"
        ordering = ['-created_at']

    def __str__(self):
        services_names = ", ".join(
            [service.name for service in self.services.all()[:3]])
        if self.services.count() > 3:
            services_names += "..."
        return f"{self.client.name} - {services_names}"

    @property
    def total_price(self):
        """Общая стоимость всех услуг в сделке"""
        return self.dealservice_set.aggregate(total=Sum('price'))['total'] or 0

    def get_services_with_prices(self):
        """Список услуг с ценами"""
        return self.dealservice_set.select_related('service').all()   

    def prices(self):
        services = self.dealservice_set.values_list('service__name', flat=True)
        return ', '.join(services)

    def add_service(self, service, price=None):
        """Добавление услуги к сделке"""
        # Локальный импорт для избежания циклической зависимости
        from .models import DealService
        DealService.objects.create(
            deal=self,
            service=service,
            price=price or service.price
        )

    def is_expired(self):
        """Проверка просрочена ли сделка"""
        return (
            timezone.now() > self.end_date
            and self.status not in ['completed', 'cancelled', 'closed']
        )


class DealService(models.Model):
    """Промежуточная модель для связи Deal-Service с индивидуальной ценой"""
    # Используем строковые ссылки вместо импорта
    deal = models.ForeignKey('Deal', on_delete=models.CASCADE,
                             verbose_name="Сделка")
    service = models.ForeignKey('price.Service', on_delete=models.CASCADE,
                                verbose_name="Услуга")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Стоимость в сделке",
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Услуга в сделке"
        verbose_name_plural = "Услуги в сделках"
        unique_together = ['deal', 'service']

    def __str__(self):
        return f"{self.deal} - {self.service.name} ({self.price} руб.)"

    def save(self, *args, **kwargs):
        """Автоподстановка цены услуги если не указана"""
        if not self.price and self.service:
            self.price = self.service.price
        super().save(*args, **kwargs)


class Comment(models.Model):
    """Комментарии к сделкам"""
    deal = models.ForeignKey('Deal', on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name="Автор")
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"
