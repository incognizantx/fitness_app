function applyTheme(color) {
    if (color === 'blue') {
        document.documentElement.style.setProperty('--primary-color', '#00aaff');
        document.documentElement.style.setProperty('--accent-color', '#0077cc');
    } else if (color === 'orange') {
        document.documentElement.style.setProperty('--primary-color', '#ff6600');
        document.documentElement.style.setProperty('--accent-color', '#cc5200');
    } else if (color === 'green') {
        document.documentElement.style.setProperty('--primary-color', '#66cc33');
        document.documentElement.style.setProperty('--accent-color', '#4d9926');
    }
}

function changeTheme(color) {
    localStorage.setItem('themeColor', color);
    applyTheme(color);
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('themeColor') || 'blue';
    const themePicker = document.getElementById('themePicker');
    if (themePicker) {
        themePicker.value = savedTheme;
    }
    applyTheme(savedTheme);
});
