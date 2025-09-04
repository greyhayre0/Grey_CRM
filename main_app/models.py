from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from django.core.validators import MinValueValidator


class Client(models.Model):
    """Модель клиента"""
    name = models.CharField(max_length=200,
                            verbose_name="ФИО клиента")
    phone = models.CharField(max_length=20,
                             verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True,
                              verbose_name="Email")
    notes = models.TextField(blank=True,
                             verbose_name="Заметки")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_total_spent(self):
        """Общая сумма потраченная клиентом
        (только завершенные и успешные сделки)"""
        total = DealService.objects.filter(
            deal__client=self,
            deal__status__in=['completed', 'successful']
        ).aggregate(total=Sum('price'))['total']
        return total or 0

    def get_deals_count(self):
        """Количество сделок клиента"""
        return self.deals.count()  # использует related_name из модели Deal

    def get_active_deals(self):
        """Активные сделки клиента"""
        return self.deals.exclude(
            status__in=['completed', 'cancelled', 'closed'])


class ServiceCategory(models.Model):
    """Категория услуг"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.IntegerField(default=0, verbose_name="Порядок сортировки")

    class Meta:
        verbose_name = "Категория услуг"
        verbose_name_plural = "Категории услуг"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """Модель услуги"""
    name = models.CharField(max_length=200,
                            verbose_name="Название услуги")
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                verbose_name="Цена")
    description = models.TextField(blank=True,
                                   verbose_name="Описание")
    duration_days = models.IntegerField(default=7,
                                        verbose_name="Срок выполнения (дней)")
    is_active = models.BooleanField(default=True,
                                    verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Дата обновления")

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория",
        related_name="services"
    )

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class Deal(models.Model):
    """Модель сделки с клиентом"""
    STATUS_CHOICES = [
        ('new', 'Принята'),
        ('in_progress', 'В работе'),
        ('ready', 'Готов к выдаче'),
        ('completed', 'Выполнена'),
        ('cancelled', 'Отменена'),
        ('successful', 'Успешная'),
        ('closed', 'Закрытая'),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name="Клиент",
        related_name='deals'  # Важно для обратной связи
    )
    services = models.ManyToManyField(
        Service,
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

    def add_service(self, service, price=None):
        """Добавление услуги к сделке"""
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
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE,
                             verbose_name="Сделка")
    service = models.ForeignKey(Service, on_delete=models.CASCADE,
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


class AdditionalContact(models.Model):
    """Дополнительные контакты для сделки"""
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE,
                             related_name="additional_contacts")
    name = models.CharField(max_length=200, verbose_name="Контактное лицо")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    class Meta:
        verbose_name = "Дополнительный контакт"
        verbose_name_plural = "Дополнительные контакты"

    def __str__(self):
        return self.name


class Comment(models.Model):
    """Комментарии к сделкам"""
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE,
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
