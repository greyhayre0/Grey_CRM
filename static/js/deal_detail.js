
function toggleEditMode() {
    const viewMode = document.querySelector('.view-mode');
    const editMode = document.querySelector('.edit-mode');
    const editBtn = document.querySelector('.edit-toggle');
            
    if (viewMode.style.display === 'none') {
        viewMode.style.display = 'block';
        editMode.style.display = 'none';
        editBtn.innerHTML = '<i class="fas fa-edit"></i> Редактировать сделку';
    } else {
        viewMode.style.display = 'none';
        editMode.style.display = 'block';
        editBtn.innerHTML = '<i class="fas fa-times"></i> Отменить редактирование';
    }
}
