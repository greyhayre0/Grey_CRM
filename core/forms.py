from datetime import timezone
from django import forms
from deals.models import Deal, DealService, Comment
from clients.models import Client
from price.models import Service
from django.core.validators import RegexValidator


class ServiceForm(forms.ModelForm):
    """
    Форма для создания и редактирования услуг
    """
    class Meta:
        model = Service
        fields = ['name', 'price', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Описание услуги...',
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Название услуги',
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': 'Цена',
                'min': '0',
                'step': '0.01',
                'class': 'form-control'
            }),
            'duration_days': forms.NumberInput(attrs={
                'placeholder': 'Дней',
                'min': '1',
                'class': 'form-control'
            }),
        }
        labels = {
            'name': 'Название услуги',
            'price': 'Цена (руб.)',
            'duration_days': 'Срок выполнения (дней)',
            'description': 'Описание',
            'is_active': 'Активна',
        }


class DealForm(forms.ModelForm):
    """
    Форма для создания сделок с обработкой клиента и услуг
    """
    # Валидатор для телефона
    phone_validator = RegexValidator(
        regex=r'^\+?[1-9]\d{1,14}$',
        message="Введите корректный номер телефона в международном формате"
    )

    # Поля для клиента
    client_name = forms.CharField(
        max_length=100,
        required=True,
        label="ФИО клиента *",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите полное имя'
        }),
        error_messages={'required': 'ФИО клиента обязательно для заполнения'}
    )

    client_phone = forms.CharField(
        max_length=20,
        required=True,
        label="Телефон клиента *",
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (900) 123-45-67'
        }),
        error_messages={
            'required': 'Телефон клиента обязателен для заполнения'}
    )

    # Скрытое поле для хранения JSON данных об услугах
    services_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        initial='[]'
    )

    class Meta:
        model = Deal
        fields = ['description', 'status', 'start_date', 'end_date']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание заказа, особые пожелания...'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': 'true'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': 'true'
            }),
        }
        labels = {
            'description': 'Описание заказа',
            'status': 'Статус сделки *',
            'start_date': 'Дата начала *',
            'end_date': 'Дата окончания *',
        }
        error_messages = {
            'start_date': {'required': 'Дата начала обязательна'},
            'end_date': {'required': 'Дата окончания обязательна'},
            'status': {'required': 'Статус сделки обязателен'},
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы, предзаполнение данных при редактировании
        """
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['client_name'].initial = self.instance.client.name
            self.fields['client_phone'].initial = self.instance.client.phone

    def clean(self):
        """
        Валидация полей
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Проверка дат
        if start_date and end_date:
            if start_date >= end_date:
                self.add_error(
                    'end_date', 'Дата окончания должна быть позже даты начала')

            # Проверка что дата начала не в прошлом
            if start_date < timezone.now():
                self.add_error(
                    'start_date', 'Дата начала не может быть в прошлом')

        return cleaned_data

    def clean_services_data(self):
        """
        Валидация данных об услугах
        """
        services_data = self.cleaned_data.get('services_data', '[]')
        try:
            import json
            services_list = json.loads(services_data)

            # Проверка что выбрана хотя бы одна услуга
            if not services_list:
                raise forms.ValidationError("Выберите хотя бы одну услугу")

            # Проверка валидности данных услуг
            for service_data in services_list:
                if not service_data.get(
                        'service_id') or not service_data.get('price'):
                    raise forms.ValidationError("Неверные данные об услугах")

        except json.JSONDecodeError:
            raise forms.ValidationError("Неверный формат данных услуг")

        return services_data

    def save(self, commit=True):
        """
        Сохранение сделки с обработкой клиента и услуг
        """
        client_name = self.cleaned_data['client_name']
        client_phone = self.cleaned_data['client_phone']

        # Создание или поиск клиента
        client, created = Client.objects.get_or_create(
            phone=client_phone,
            defaults={'name': client_name}
        )

        # Обновление имени если клиент уже существует
        if not created and client.name != client_name:
            client.name = client_name
            client.save()

        # Сохранение сделки
        deal = super().save(commit=False)
        deal.client = client

        if commit:
            deal.save()

            # Обработка услуг
            services_data = self.cleaned_data.get('services_data')
            if services_data:
                import json
                try:
                    services_list = json.loads(services_data)

                    # Удаление старых услуг
                    deal.dealservice_set.all().delete()

                    # Добавление новых услуг
                    for service_data in services_list:
                        service_id = service_data.get('service_id')
                        price = service_data.get('price')

                        if service_id and price:
                            service = Service.objects.get(id=service_id)
                            DealService.objects.create(
                                deal=deal,
                                service=service,
                                price=price
                            )

                except (json.JSONDecodeError, Service.DoesNotExist) as e:
                    raise forms.ValidationError(
                        f"Ошибка обработки услуг: {str(e)}")

        return deal


class ClientForm(forms.ModelForm):
    """
    Форма для создания и редактирования клиентов
    """
    class Meta:
        model = Client
        fields = ['name', 'phone', 'email', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ФИО клиента'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (900) 123-45-67'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительная информация о клиенте...'
            }),
        }
        labels = {
            'name': 'ФИО клиента',
            'phone': 'Телефон',
            'email': 'Email',
            'notes': 'Заметки',
        }


class CommentForm(forms.ModelForm):
    """
    Форма для добавления комментариев к сделкам
    """
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Добавить комментарий...',
                'rows': 3
            }),
        }
        labels = {
            'text': 'Комментарий',
        }


class DealEditForm(forms.ModelForm):
    """
    Форма для редактирования существующей сделки (без изменения клиента)
    """
    class Meta:
        model = Deal
        fields = ['description', 'status', 'start_date', 'end_date']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание заказа...'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }
        labels = {
            'description': 'Описание заказа',
            'status': 'Статус сделки',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
        }
