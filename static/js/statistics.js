<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
// Данные для графиков из Django контекста
const monthlyData = {
    labels: {{ monthly_labels|safe }},
    datasets: [{
        label: 'Количество сделок',
        data: {{ monthly_data|safe }},
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        tension: 0.3
    }]
};

const servicesData = {
    labels: {{ services_labels|safe }},
    datasets: [{
        data: {{ services_data|safe }},
        backgroundColor: [
            'rgba(255, 99, 132, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)'
        ],
        borderWidth: 1
    }]
};

// Инициализация графиков при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
            
    // Обработчик изменения периода
    document.getElementById('periodSelect').addEventListener('change', function() {
        updateCharts(this.value);
    });
});

function initCharts() {
    // Линейный график
    const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
    new Chart(monthlyCtx, {
        type: 'line',
        data: monthlyData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Динамика сделок по месяцам'
                }
            }
        }
    });

    // Круговая диаграмма
    const servicesCtx = document.getElementById('servicesChart').getContext('2d');
    new Chart(servicesCtx, {
        type: 'pie',
        data: servicesData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: 'Распределение по услугам'
                }
            }
        }
    });
}

function updateCharts(period) {
    // AJAX запрос для обновления данных
    fetch(`/statistics/update/?period=${period}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        // Обновление данных графиков
        monthlyData.labels = data.monthly_labels;
        monthlyData.datasets[0].data = data.monthly_data;
                
        servicesData.labels = data.services_labels;
        servicesData.datasets[0].data = data.services_data;
                
        // Перерисовка графиков
        initCharts();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
