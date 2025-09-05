
// CSRF token для AJAX запросов
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initServiceModals();
    initViewToggle();
    initSearch();
});

function initServiceModals() {
    // Модальное окно для услуги
    const serviceModal = document.getElementById('serviceModal');
    const addServiceBtn = document.getElementById('addServiceBtn');
    const cancelServiceBtn = document.getElementById('cancelServiceBtn');
    const serviceForm = document.getElementById('serviceForm');
            
    if (addServiceBtn) {
        addServiceBtn.addEventListener('click', () => {
            document.getElementById('modalServiceTitle').textContent = 'Добавить услугу';
            document.getElementById('serviceId').value = '';
            document.getElementById('serviceForm').reset();
            serviceModal.style.display = 'flex';
        });
    }
            
    if (cancelServiceBtn) {
        cancelServiceBtn.addEventListener('click', () => {
            serviceModal.style.display = 'none';
        });
    }
            
    // Закрытие модальных окон
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
            
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal').style.display = 'none';
        });
    });
            
    // Обработка формы
    if (serviceForm) {
        serviceForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveService();
        });
    }
}

function initViewToggle() {
    const viewButtons = document.querySelectorAll('.view-btn');
    const servicesView = document.getElementById('servicesView');
            
    viewButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const viewType = this.getAttribute('data-view');
                    
            // Обновляем активную кнопку
            viewButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
                    
            // Меняем вид
            servicesView.className = viewType === 'grid' ? 'services-grid' : 'services-list';
        });
    });
}

function initSearch() {
    const searchInput = document.getElementById('searchInput');
    let searchTimeout;
            
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const searchValue = this.value.trim();
            let url = '?';
            if (searchValue) url += `search=${encodeURIComponent(searchValue)}`;
            window.location.href = url || '?';
        }, 500);
    });
}
        
function editService(serviceId) {
    // Загрузка данных услуги через AJAX
    fetch(`/api/services/${serviceId}/`)
        .then(response => response.json())
        .then(service => {
            document.getElementById('modalServiceTitle').textContent = 'Редактировать услугу';
            document.getElementById('serviceId').value = service.id;
            document.getElementById('serviceName').value = service.name;
            document.getElementById('serviceDescription').value = service.description || '';
            document.getElementById('servicePrice').value = service.price;
            document.getElementById('serviceDuration').value = service.duration;
            document.getElementById('serviceCategory').value = service.category || '';
            document.getElementById('serviceStatus').value = service.is_active.toString();
            document.getElementById('serviceMaterials').value = service.materials || '';
            document.getElementById('serviceModal').style.display = 'flex';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при загрузке данных услуги');
        });
}

function saveService() {
    const formData = new FormData(document.getElementById('serviceForm'));
    const serviceId = formData.get('service_id');
            
    // ИСПРАВЛЕННЫЙ URL - добавлен префикс /crm/
    const url = '/crm/api/services/' + (serviceId ? serviceId + '/' : '');
    const method = serviceId ? 'PUT' : 'POST';
            
    // Преобразуем FormData в объект
    const data = {
        'name': formData.get('name'),
        'price': parseFloat(formData.get('price')) || 0,
        'description': formData.get('description') || '',
        'duration_days': parseInt(formData.get('duration_days')) || 7,
        'is_active': formData.get('is_active') === 'true'
    };
            
    console.log('Отправка запроса на:', url, 'с данными:', data);
            
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Услуга успешно сохранена!');
            document.getElementById('serviceModal').style.display = 'none';
            location.reload();
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при сохранении услуги: ' + error.message);
    });
}

function toggleService(serviceId) {
    if (confirm('Изменить статус услуги?')) {
        fetch(`crm/api/services/${serviceId}/toggle/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Статус услуги изменен!');
                location.reload();
            } else {
                alert('Ошибка: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при изменении статуса');
        });
    }
}

function deleteService(serviceId) {
    if (confirm('Вы уверены, что хотите удалить эту услугу?')) {
        fetch(`crm/api/services/${serviceId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Услуга удалена!');
                location.reload();
            } else {
                alert('Ошибка: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при удалении услуги');
        });
    }
}

function exportPriceList() {
    window.open('crm/services/export/pdf/', '_blank');
}

function printPriceList() {
    window.print();
}
