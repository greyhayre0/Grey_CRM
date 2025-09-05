
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
            const searchValue = this.value.trim();
            const statusFilter = document.getElementById('statusFilter').value;
            const dateFilter = document.getElementById('dateFilter').value;
                    
            let url = `?`;
            if (searchValue) url += `search=${encodeURIComponent(searchValue)}&`;
            if (statusFilter !== 'all') url += `status=${statusFilter}&`;
            if (dateFilter !== 'all') url += `date=${dateFilter}&`;
                    
            // Убираем последний & если он есть
            if (url.endsWith('&')) url = url.slice(0, -1);
            if (url.endsWith('?')) url = url.slice(0, -1);
                    
            window.location.href = url || '?';
        }, 500);
    });

    // Фильтры
    document.getElementById('statusFilter').addEventListener('change', updateFilters);
    document.getElementById('dateFilter').addEventListener('change', updateFilters);

    function updateFilters() {
        const searchValue = searchInput.value.trim();
        const statusFilter = document.getElementById('statusFilter').value;
        const dateFilter = document.getElementById('dateFilter').value;
                
        let url = `?`;
        if (searchValue) url += `search=${encodeURIComponent(searchValue)}&`;
        if (statusFilter !== 'all') url += `status=${statusFilter}&`;
        if (dateFilter !== 'all') url += `date=${dateFilter}&`;
                
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

// Функция восстановления сделки
function restoreDeal(dealId) {
    if (confirm('Восстановить эту сделку?')) {
        fetch(`/deal/${dealId}/restore/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Сделка успешно восстановлена!');
                location.reload();
            } else {
                alert('Ошибка при восстановлении сделки: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при восстановлении сделки');
        });
    }
}

// Функция удаления сделки
function deleteDeal(dealId) {
    if (confirm('Вы уверены, что хотите окончательно удалить эту сделку? Это действие нельзя отменить.')) {
        fetch(`/deal/${dealId}/delete/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Сделка успешно удалена!');
                // Удаляем строку из таблицы
                document.querySelector(`.deal-row[data-id="${dealId}"]`).remove();
                        
                // Если строк не осталось, показываем сообщение
                if (document.querySelectorAll('.deal-row').length === 0) {
                    location.reload();
                }
            } else {
                alert('Ошибка при удалении сделки: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при удалении сделки');
        });
    }
}
