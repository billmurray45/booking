/**
 * Register Page Script
 */

document.addEventListener('DOMContentLoaded', function() {
    // Redirect if already authenticated
    redirectIfAuthenticated();

    const registerForm = document.getElementById('register-form');
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');
    const registerBtn = document.getElementById('register-btn');

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Hide previous messages
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';

        // Get form data
        const formData = {
            username: document.getElementById('username').value.trim(),
            email: document.getElementById('email').value.trim(),
            first_name: document.getElementById('first_name').value.trim(),
            last_name: document.getElementById('last_name').value.trim(),
            phone: document.getElementById('phone').value.trim(),
            password: document.getElementById('password').value,
            password_confirm: document.getElementById('password_confirm').value
        };

        // Basic client-side validation
        if (formData.password !== formData.password_confirm) {
            errorMessage.textContent = 'Пароли не совпадают';
            errorMessage.style.display = 'block';
            return;
        }

        if (formData.password.length < 8) {
            errorMessage.textContent = 'Пароль должен содержать минимум 8 символов';
            errorMessage.style.display = 'block';
            return;
        }

        // Disable button during request
        registerBtn.disabled = true;
        registerBtn.textContent = 'Регистрация...';

        try {
            const response = await API.register(formData);

            if (response.ok) {
                const data = await response.json();

                // Save tokens
                setTokens(data.tokens.access, data.tokens.refresh);

                // Show success message
                successMessage.textContent = 'Регистрация успешна! Перенаправление...';
                successMessage.style.display = 'block';

                // Redirect to profile after 1 second
                setTimeout(() => {
                    window.location.href = '/profile/';
                }, 1000);
            } else {
                const data = await response.json();

                // Display error messages
                let errorText = 'Ошибка регистрации:';
                if (typeof data === 'object') {
                    for (const [field, errors] of Object.entries(data)) {
                        if (Array.isArray(errors)) {
                            errorText += `\n${field}: ${errors.join(', ')}`;
                        } else {
                            errorText += `\n${field}: ${errors}`;
                        }
                    }
                } else {
                    errorText = data.detail || 'Произошла ошибка при регистрации';
                }

                errorMessage.textContent = errorText;
                errorMessage.style.display = 'block';
                errorMessage.style.whiteSpace = 'pre-line';

                // Re-enable button
                registerBtn.disabled = false;
                registerBtn.textContent = 'Зарегистрироваться';
            }
        } catch (error) {
            console.error('Registration error:', error);
            errorMessage.textContent = 'Ошибка соединения с сервером';
            errorMessage.style.display = 'block';

            // Re-enable button
            registerBtn.disabled = false;
            registerBtn.textContent = 'Зарегистрироваться';
        }
    });
});
