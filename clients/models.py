from django.db import models
from django.db.models import Sum


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
        # Локальный импорт для избежания циклической зависимости
        from deals.models import DealService

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


class AdditionalContact(models.Model):
    """Дополнительные контакты для сделки"""
    # Используем строковую ссылку вместо импорта
    deal = models.ForeignKey('deals.Deal', on_delete=models.CASCADE,
                             related_name="additional_contacts")
    name = models.CharField(max_length=200, verbose_name="Контактное лицо")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    class Meta:
        verbose_name = "Дополнительный контакт"
        verbose_name_plural = "Дополнительные контакты"

    def __str__(self):
        return self.name
