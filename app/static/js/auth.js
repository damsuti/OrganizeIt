document.getElementById('to-register').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('login-area').classList.add('hidden');
    document.getElementById('register-area').classList.remove('hidden');
    clearAlert();
});

document.getElementById('to-login').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('register-area').classList.add('hidden');
    document.getElementById('login-area').classList.remove('hidden');
    clearAlert();
});

function showAlert(message, type) {
    const alertBox = document.getElementById('alert-box');
    alertBox.className = `alert alert-${type}`;
    alertBox.innerText = message;
    alertBox.classList.remove('hidden');
}

function clearAlert() {
    document.getElementById('alert-box').classList.add('hidden');
}

// Submissão do Registro
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    const response = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await response.get_json ? await response.get_json() : await response.json();

    if (response.ok) {
        showAlert(data.success, 'success');
        document.getElementById('register-form').reset();
        setTimeout(() => document.getElementById('to-login').click(), 1500);
    } else {
        showAlert(data.error, 'danger');
    }
});

// Submissão do Login
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await response.get_json ? await response.get_json() : await response.json();

    if (response.ok) {
        showAlert(data.success, 'success');
        // Redireciona de verdade para a nossa nova homepage dinâmica!
        setTimeout(() => window.location.href = data.redirect, 800);
    } else {
        showAlert(data.error, 'danger');
    }
});