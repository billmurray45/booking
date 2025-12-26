/**
 * Login Page Script
 */

document.addEventListener('DOMContentLoaded', function() {
    // Redirect if already authenticated
    redirectIfAuthenticated();

    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');
    const loginBtn = document.getElementById('login-btn');

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Hide previous messages
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';

        // Get form data
        const formData = {
            username: document.getElementById('username').value.trim(),
            password: document.getElementById('password').value
        };

        // Basic client-side validation
        if (!formData.username || !formData.password) {
            errorMessage.textContent = 'Пожалуйста, заполните все поля';
            errorMessage.style.display = 'block';
            return;
        }

        // Disable button during request
        loginBtn.disabled = true;
        loginBtn.textContent = 'Вход...';

        try {
            const response = await API.login(formData);

            if (response.ok) {
                const data = await response.json();

                // Save tokens (simplejwt returns {access, refresh} directly)
                setTokens(data.access, data.refresh);

                // Show success message
                successMessage.textContent = 'Вход выполнен! Перенаправление...';
                successMessage.style.display = 'block';

                // Redirect to profile after 1 second
                setTimeout(() => {
                    window.location.href = '/profile/';
                }, 1000);
            } else {
                const data = await response.json();

                // Display error message
                let errorText = data.detail || 'Неверные учетные данные';
                if (typeof data === 'object' && !data.detail) {
                    errorText = 'Ошибка входа:';
                    for (const [field, errors] of Object.entries(data)) {
                        if (Array.isArray(errors)) {
                            errorText += `\n${errors.join(', ')}`;
                        } else {
                            errorText += `\n${errors}`;
                        }
                    }
                }

                errorMessage.textContent = errorText;
                errorMessage.style.display = 'block';
                errorMessage.style.whiteSpace = 'pre-line';

                // Re-enable button
                loginBtn.disabled = false;
                loginBtn.textContent = 'Войти';
            }
        } catch (error) {
            console.error('Login error:', error);
            errorMessage.textContent = 'Ошибка соединения с сервером';
            errorMessage.style.display = 'block';

            // Re-enable button
            loginBtn.disabled = false;
            loginBtn.textContent = 'Войти';
        }
    });
});
