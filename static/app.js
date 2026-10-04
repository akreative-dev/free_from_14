document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('clear-btn');

    if (btn) {
        btn.addEventListener('click', function () {
            window.location.href = '/';
        });
    }
});
