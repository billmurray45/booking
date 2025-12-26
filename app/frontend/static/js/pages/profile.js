/**
 * Profile Page Script
 */

document.addEventListener('DOMContentLoaded', function() {
    // Require authentication
    requireAuth();

    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');

    // Profile viewing elements
    const profileInfo = document.getElementById('profile-info');
    const editProfileBtn = document.getElementById('edit-profile-btn');

    // Profile editing elements
    const editProfileSection = document.getElementById('edit-profile-section');
    const editProfileForm = document.getElementById('edit-profile-form');
    const cancelEditBtn = document.getElementById('cancel-edit-btn');
    const saveProfileBtn = document.getElementById('save-profile-btn');

    // Password change elements
    const changePasswordBtn = document.getElementById('change-password-btn');
    const changePasswordForm = document.getElementById('change-password-form');
    const cancelPasswordBtn = document.getElementById('cancel-password-btn');
    const savePasswordBtn = document.getElementById('save-password-btn');

    let currentUserData = null;

    // Load user profile on page load
    loadProfile();

    // Edit profile button click
    editProfileBtn.addEventListener('click', function() {
        profileInfo.parentElement.style.display = 'none';
        editProfileSection.style.display = 'block';
        populateEditForm();
    });

    // Cancel edit button click
    cancelEditBtn.addEventListener('click', function() {
        editProfileSection.style.display = 'none';
        profileInfo.parentElement.style.display = 'block';
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';
    });

    // Edit profile form submit
    editProfileForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';

        const formData = {
            email: document.getElementById('edit-email').value.trim(),
            first_name: document.getElementById('edit-first-name').value.trim(),
            last_name: document.getElementById('edit-last-name').value.trim(),
            phone: document.getElementById('edit-phone').value.trim()
        };

        saveProfileBtn.disabled = true;
        saveProfileBtn.textContent = 'Сохранение...';

        try {
            const response = await API.updateProfile(formData);

            if (response.ok) {
                const data = await response.json();
                currentUserData = data;

                successMessage.textContent = 'Профиль успешно обновлен!';
                successMessage.style.display = 'block';

                // Update display
                displayProfile(data);

                // Hide edit form after 1 second
                setTimeout(() => {
                    editProfileSection.style.display = 'none';
                    profileInfo.parentElement.style.display = 'block';
                    successMessage.style.display = 'none';
                }, 1500);
            } else {
                const data = await response.json();

                let errorText = 'Ошибка обновления профиля:';
                if (typeof data === 'object') {
                    for (const [field, errors] of Object.entries(data)) {
                        if (Array.isArray(errors)) {
                            errorText += `\n${field}: ${errors.join(', ')}`;
                        } else {
                            errorText += `\n${field}: ${errors}`;
                        }
                    }
                } else {
                    errorText = data.detail || 'Произошла ошибка';
                }

                errorMessage.textContent = errorText;
                errorMessage.style.display = 'block';
                errorMessage.style.whiteSpace = 'pre-line';
            }
        } catch (error) {
            console.error('Profile update error:', error);
            errorMessage.textContent = 'Ошибка соединения с сервером';
            errorMessage.style.display = 'block';
        } finally {
            saveProfileBtn.disabled = false;
            saveProfileBtn.textContent = 'Сохранить';
        }
    });

    // Change password button click
    changePasswordBtn.addEventListener('click', function() {
        changePasswordForm.style.display = 'block';
        changePasswordBtn.style.display = 'none';
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';
    });

    // Cancel password change button click
    cancelPasswordBtn.addEventListener('click', function() {
        changePasswordForm.style.display = 'none';
        changePasswordBtn.style.display = 'block';
        changePasswordForm.reset();
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';
    });

    // Change password form submit
    changePasswordForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';

        const oldPassword = document.getElementById('old-password').value;
        const newPassword = document.getElementById('new-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        // Client-side validation
        if (newPassword !== confirmPassword) {
            errorMessage.textContent = 'Новые пароли не совпадают';
            errorMessage.style.display = 'block';
            return;
        }

        if (newPassword.length < 8) {
            errorMessage.textContent = 'Новый пароль должен содержать минимум 8 символов';
            errorMessage.style.display = 'block';
            return;
        }

        const formData = {
            old_password: oldPassword,
            new_password: newPassword,
            new_password_confirm: confirmPassword
        };

        savePasswordBtn.disabled = true;
        savePasswordBtn.textContent = 'Сохранение...';

        try {
            const response = await API.changePassword(formData);

            if (response.ok) {
                successMessage.textContent = 'Пароль успешно изменен!';
                successMessage.style.display = 'block';

                // Reset and hide form after 1 second
                setTimeout(() => {
                    changePasswordForm.reset();
                    changePasswordForm.style.display = 'none';
                    changePasswordBtn.style.display = 'block';
                    successMessage.style.display = 'none';
                }, 1500);
            } else {
                const data = await response.json();

                let errorText = data.detail || 'Ошибка смены пароля';
                if (typeof data === 'object' && !data.detail) {
                    errorText = 'Ошибка:';
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
            }
        } catch (error) {
            console.error('Password change error:', error);
            errorMessage.textContent = 'Ошибка соединения с сервером';
            errorMessage.style.display = 'block';
        } finally {
            savePasswordBtn.disabled = false;
            savePasswordBtn.textContent = 'Сохранить пароль';
        }
    });

    // Helper functions
    async function loadProfile() {
        try {
            const response = await API.getProfile();

            if (response.ok) {
                const data = await response.json();
                currentUserData = data;
                displayProfile(data);
            } else {
                errorMessage.textContent = 'Не удалось загрузить профиль';
                errorMessage.style.display = 'block';
            }
        } catch (error) {
            console.error('Profile load error:', error);
            errorMessage.textContent = 'Ошибка загрузки профиля';
            errorMessage.style.display = 'block';
        }
    }

    function displayProfile(data) {
        document.getElementById('display-username').textContent = data.username || '-';
        document.getElementById('display-email').textContent = data.email || '-';
        document.getElementById('display-first-name').textContent = data.first_name || '-';
        document.getElementById('display-last-name').textContent = data.last_name || '-';
        document.getElementById('display-phone').textContent = data.phone || '-';

        // Format date
        if (data.date_joined) {
            const date = new Date(data.date_joined);
            document.getElementById('display-date-joined').textContent = date.toLocaleDateString('ru-RU');
        } else {
            document.getElementById('display-date-joined').textContent = '-';
        }
    }

    function populateEditForm() {
        if (currentUserData) {
            document.getElementById('edit-email').value = currentUserData.email || '';
            document.getElementById('edit-first-name').value = currentUserData.first_name || '';
            document.getElementById('edit-last-name').value = currentUserData.last_name || '';
            document.getElementById('edit-phone').value = currentUserData.phone || '';
        }
    }
});
