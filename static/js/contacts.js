
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация модального окна клиента
    const clientModal = document.getElementById('clientModal');
    const addClientBtn = document.getElementById('addClientBtn');
    const cancelClientBtn = document.getElementById('cancelClientBtn');
            
    if (addClientBtn) {
        addClientBtn.addEventListener('click', () => {
            clientModal.style.display = 'flex';
        });
    }
            
    if (cancelClientBtn) {
        cancelClientBtn.addEventListener('click', () => {
            clientModal.style.display = 'none';
        });
    }
            
    // Поиск клиентов
    const clientSearch = document.getElementById('clientSearch');
    if (clientSearch) {
        clientSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const clientCards = document.querySelectorAll('.client-card');
                    
            clientCards.forEach(card => {
                const clientName = card.querySelector('.client-name').textContent.toLowerCase();
                const clientPhone = card.querySelector('.client-phone').textContent.toLowerCase();
                        
                if (clientName.includes(searchTerm) || clientPhone.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
            
    // Обработчики для карточек клиентов
    document.querySelectorAll('.client-card').forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.client-actions')) {
                const clientId = this.getAttribute('data-client-id');
                window.location.href = `/crm/client/${clientId}/`;
            }
        });
    });
});
