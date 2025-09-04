function normalizePath(path) {
    // Добавляем слэш в конец, если его нет, кроме корня '/'
    if (path === '/') return path;
    return path.endsWith('/') ? path : path + '/';
}

document.addEventListener('DOMContentLoaded', () => {
    const navButtons = document.querySelectorAll('.nav-btn');
    const currentPath = normalizePath(window.location.pathname);

    navButtons.forEach(button => button.classList.remove('active'));

    for (const button of navButtons) {
        let href = button.getAttribute('href');
        if (!href) continue;
        href = normalizePath(href);

        if (href === '/' && currentPath === '/') {
            // Главная страница — строгое равенство
            button.classList.add('active');
            break;
        }
        else if (href === '/crm/' && currentPath === '/crm/') {
            // Ваш корень /crm/ — строгое равенство
            button.classList.add('active');
            break;
        }
        else if (href !== '/' && href !== '/crm/' && currentPath.startsWith(href)) {
            // Для остальных разделов — startsWith
            button.classList.add('active');
            break;
        }
    }
});
