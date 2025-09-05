from django.db import models


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
