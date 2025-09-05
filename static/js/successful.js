
// CSRF token для AJAX запросов
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Поиск
    const searchInput = document.getElementById('searchInput');
    let searchTimeout;
            
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            updateFilters();
        }, 500);
    });

    // Фильтры
    document.getElementById('serviceFilter').addEventListener('change', updateFilters);
    document.getElementById('dateFilter').addEventListener('change', updateFilters);
    document.getElementById('sortBy').addEventListener('change', updateFilters);

    function updateFilters() {
        const searchValue = searchInput.value.trim();
        const serviceFilter = document.getElementById('serviceFilter').value;
        const dateFilter = document.getElementById('dateFilter').value;
        const sortBy = document.getElementById('sortBy').value;
                
        let url = `?`;
        if (searchValue) url += `search=${encodeURIComponent(searchValue)}&`;
        if (serviceFilter !== 'all') url += `service=${serviceFilter}&`;
        if (dateFilter !== 'all') url += `date=${dateFilter}&`;
        if (sortBy !== 'newest') url += `sort=${sortBy}&`;
                
        // Убираем последний & если он есть
        if (url.endsWith('&')) url = url.slice(0, -1);
        if (url.endsWith('?')) url = url.slice(0, -1);
                
        window.location.href = url || '?';
    }
});

// Функция просмотра сделки
function viewDeal(dealId) {
    window.location.href = `/deal/${dealId}/`;
}

// Функция повторения сделки
function repeatDeal(dealId) {
    if (confirm('Создать новую сделку на основе этой?')) {
        fetch(`/deal/${dealId}/repeat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Новая сделка создана успешно!');
                window.location.href = '/'; // Перенаправляем на главную
            } else {
                alert('Ошибка при создании сделки: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при создании сделки');
        });
    }
}

// Функция отправки email
function sendEmail(dealId) {
    const emailSubject = encodeURIComponent('Благодарим за сотрудничество!');
    const emailBody = encodeURIComponent('Уважаемый клиент, благодарим вас за выбор наших услуг!');
            
    window.location.href = `mailto:?subject=${emailSubject}&body=${emailBody}`;
}

// Функция экспорта данных
function exportData(format) {
    const searchValue = document.getElementById('searchInput').value.trim();
    const serviceFilter = document.getElementById('serviceFilter').value;
    const dateFilter = document.getElementById('dateFilter').value;
    const sortBy = document.getElementById('sortBy').value;
            
    let url = `/successful/deals/export/${format}/?`;
    if (searchValue) url += `search=${encodeURIComponent(searchValue)}&`;
    if (serviceFilter !== 'all') url += `service=${serviceFilter}&`;
    if (dateFilter !== 'all') url += `date=${dateFilter}&`;
    if (sortBy !== 'newest') url += `sort=${sortBy}&`;
            
    // Убираем последний & если он есть
    if (url.endsWith('&')) url = url.slice(0, -1);
    if (url.endsWith('?')) url = url.slice(0, -1);
            
    window.open(url, '_blank');
}