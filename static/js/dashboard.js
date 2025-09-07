// CSRF token для AJAX запросов
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
let currentDealId = null;

// --- Функции для работы с услугами ---

function addService() {
    const servicesContainer = document.getElementById('servicesContainer');
    const serviceItem = document.createElement('div');
    serviceItem.className = 'service-item';

    serviceItem.innerHTML = `
        <select name="services[]" class="service-select" onchange="updateServicePrice(this)">
            <option value="">Выберите услугу</option>
            {% for service in services %}
            <option value="{{ service.id }}" data-price="{{ service.price }}">
                {{ service.name }} - {{ service.price }} руб.
            </option>
            {% endfor %}
        </select>
        <input type="number" name="prices[]" placeholder="Цена" class="service-price" onchange="calculateTotal()">
        <button type="button" class="remove-service" onclick="removeService(this)">×</button>
    `;

    servicesContainer.appendChild(serviceItem);
    calculateTotal();
}

function removeService(button) {
    const serviceItem = button.closest('.service-item');
    if (serviceItem) {
        serviceItem.remove();
        calculateTotal();
    }
}

function updateServicePrice(select) {
    const priceInput = select.parentElement.querySelector('.service-price');
    const price = select.options[select.selectedIndex].getAttribute('data-price');
    if (price) {
        priceInput.value = price;
    } else {
        priceInput.value = '';
    }
    calculateTotal();
}

function calculateTotal() {
    let total = 0;
    document.querySelectorAll('.service-price').forEach(input => {
        const val = parseFloat(input.value);
        if (!isNaN(val)) {
            total += val;
        }
    });
    document.getElementById('totalPrice').textContent = `Итого: ${total} руб.`;
}

// --- Функции для работы со статусами ---

function markAsSuccessful(dealId) {
    updateDealStatusDirect(dealId, 'successful');
}

function markAsClosed(dealId) {
    updateDealStatusDirect(dealId, 'closed');
}

function showStatusModal(dealId) {
    currentDealId = dealId;
    document.getElementById('statusDealId').value = dealId;
    document.getElementById('statusModal').style.display = 'flex';
}

function closeStatusModal() {
    document.getElementById('statusModal').style.display = 'none';
}

function updateDealStatus() {
    const status = document.getElementById('newStatus').value;
    updateDealStatusDirect(currentDealId, status);
}

function updateDealStatusDirect(dealId, status) {
    fetch(`/crm/deal/${dealId}/update_status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification(`Статус изменен на: ${data.status_display}`, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showNotification(`Ошибка: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при обновлении статуса', 'error');
    });
}

// --- Инициализация при загрузке страницы ---

document.addEventListener('DOMContentLoaded', () => {
    initModals();
    setCurrentDate();
    calculateTotal();

    // Обработчики для карточек сделок
    document.querySelectorAll('.deal-card').forEach(card => {
        card.addEventListener('click', e => {
            if (!e.target.closest('.deal-actions')) {
                const dealId = card.getAttribute('data-id');
                window.location.href = `/crm/deal/${dealId}/`;
            }
        });
    });
});

// --- Функции инициализации модальных окон ---

function initModals() {
    const dealModal = document.getElementById('dealModal');
    const addDealBtn = document.getElementById('addDealBtn');
    const cancelDealBtn = document.getElementById('cancelDealBtn');

    if (addDealBtn) {
        addDealBtn.addEventListener('click', () => {
            dealModal.style.display = 'flex';
        });
    }

    if (cancelDealBtn) {
        cancelDealBtn.addEventListener('click', () => {
            dealModal.style.display = 'none';
        });
    }

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', e => {
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
}

// --- Установка текущей даты и даты через неделю ---

function setCurrentDate() {
    const today = new Date();
    const nextWeek = new Date();
    nextWeek.setDate(today.getDate() + 7);

    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');

    if (startDate) startDate.valueAsDate = today;
    if (endDate) endDate.valueAsDate = nextWeek;
}

// --- Функция для показа уведомлений ---

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        z-index: 10000;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        max-width: 300px;
        opacity: 1;
        transition: opacity 0.5s;
    `;

    switch (type) {
        case 'success':
            notification.style.backgroundColor = '#28a745';
            break;
        case 'error':
            notification.style.backgroundColor = '#dc3545';
            break;
        default:
            notification.style.backgroundColor = '#17a2b8';
    }

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 500);
    }, 3000);
}

function openDealDetails(dealId) {
    // Перенаправляем на страницу деталей сделки
    window.location.href = `/deal/${dealId}/`;
}