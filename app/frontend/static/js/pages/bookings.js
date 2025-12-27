/**
 * Bookings Page Script - Управление бронированиями
 */

document.addEventListener('DOMContentLoaded', function() {
    // Проверка авторизации
    if (!isAuthenticated()) {
        window.location.href = '/login/';
        return;
    }

    const bookingsList = document.getElementById('bookings-list');
    const loadingMessage = document.getElementById('loading-message');
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');
    const emptyState = document.getElementById('empty-state');

    // Фильтры
    const statusFilter = document.getElementById('status-filter');
    const timeFilter = document.getElementById('time-filter');
    const sortFilter = document.getElementById('sort-filter');
    const applyFiltersBtn = document.getElementById('apply-filters');
    const resetFiltersBtn = document.getElementById('reset-filters');

    // Модальное окно редактирования
    const editModal = document.getElementById('edit-modal');
    const editForm = document.getElementById('edit-booking-form');
    const editError = document.getElementById('edit-error');

    // Загрузка бронирований при загрузке страницы
    loadBookings();

    // Обработчики событий
    applyFiltersBtn.addEventListener('click', loadBookings);
    resetFiltersBtn.addEventListener('click', resetFilters);
    editForm.addEventListener('submit', handleEditSubmit);

    /**
     * Загрузка списка бронирований
     */
    async function loadBookings() {
        // Скрываем все блоки
        bookingsList.style.display = 'none';
        emptyState.style.display = 'none';
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';
        loadingMessage.style.display = 'block';

        try {
            const params = buildParams();
            const response = await API.getBookings(params);

            if (response.ok) {
                const data = await response.json();
                displayBookings(data.results || data);
                loadingMessage.style.display = 'none';
            } else if (response.status === 401) {
                window.location.href = '/login/';
            } else {
                throw new Error('Ошибка загрузки бронирований');
            }
        } catch (error) {
            console.error('Error loading bookings:', error);
            loadingMessage.style.display = 'none';
            showError('Не удалось загрузить бронирования. Попробуйте позже.');
        }
    }

    /**
     * Построение параметров фильтрации
     */
    function buildParams() {
        const params = {};

        // Статус
        if (statusFilter.value) {
            params.status = statusFilter.value;
        }

        // Временной период
        if (timeFilter.value) {
            params[`is_${timeFilter.value}`] = 'true';
        }

        // Сортировка
        if (sortFilter.value) {
            params.ordering = sortFilter.value;
        }

        return params;
    }

    /**
     * Отображение списка бронирований
     */
    function displayBookings(bookings) {
        bookingsList.innerHTML = '';

        if (!bookings || bookings.length === 0) {
            emptyState.style.display = 'block';
            bookingsList.style.display = 'none';
            return;
        }

        bookings.forEach(booking => {
            const bookingCard = createBookingCard(booking);
            bookingsList.appendChild(bookingCard);
        });

        bookingsList.style.display = 'block';
    }

    /**
     * Создание карточки бронирования
     */
    function createBookingCard(booking) {
        const card = document.createElement('div');
        card.className = 'booking-card';

        // Статус бэдж
        const statusClass = booking.status === 'active' ? 'status-active' : 'status-cancelled';
        const statusText = booking.status === 'active' ? 'Активно' : 'Отменено';

        // Определяем временной статус
        const today = new Date().toISOString().split('T')[0];
        let timeStatus = '';
        if (booking.check_out < today) {
            timeStatus = '<span class="time-badge time-past">Прошедшее</span>';
        } else if (booking.check_in > today) {
            timeStatus = '<span class="time-badge time-upcoming">Будущее</span>';
        } else {
            timeStatus = '<span class="time-badge time-current">Текущее</span>';
        }

        // Форматируем даты
        const checkIn = formatDate(booking.check_in);
        const checkOut = formatDate(booking.check_out);
        const createdAt = formatDateTime(booking.created_at);

        // Кнопки действий (только для активных бронирований)
        let actions = '';
        if (booking.status === 'active' && booking.check_in >= today) {
            actions = `
                <div class="booking-actions">
                    <button class="btn btn-sm btn-primary" onclick="openEditModal(${booking.id}, '${booking.check_in}', '${booking.check_out}')">
                        Изменить даты
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="cancelBooking(${booking.id})">
                        Отменить
                    </button>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="booking-card-header">
                <div>
                    <h3 class="booking-room">Комната ${booking.room_number || booking.room?.room_number || 'N/A'}</h3>
                    <span class="booking-status ${statusClass}">${statusText}</span>
                    ${timeStatus}
                </div>
                <div class="booking-id">#${booking.id}</div>
            </div>

            <div class="booking-card-body">
                <div class="booking-details">
                    <div class="booking-detail">
                        <span class="detail-label">Дата заезда:</span>
                        <span class="detail-value">${checkIn}</span>
                    </div>
                    <div class="booking-detail">
                        <span class="detail-label">Дата выезда:</span>
                        <span class="detail-value">${checkOut}</span>
                    </div>
                    <div class="booking-detail">
                        <span class="detail-label">Количество ночей:</span>
                        <span class="detail-value">${booking.nights_count}</span>
                    </div>
                    <div class="booking-detail">
                        <span class="detail-label">Общая стоимость:</span>
                        <span class="detail-value detail-price">${formatPrice(booking.total_price)}</span>
                    </div>
                    <div class="booking-detail">
                        <span class="detail-label">Дата создания:</span>
                        <span class="detail-value">${createdAt}</span>
                    </div>
                </div>

                ${actions}
            </div>
        `;

        return card;
    }

    /**
     * Отмена бронирования
     */
    window.cancelBooking = async function(bookingId) {
        if (!confirm('Вы уверены, что хотите отменить это бронирование?')) {
            return;
        }

        try {
            const response = await API.cancelBooking(bookingId);

            if (response.ok) {
                const data = await response.json();
                showSuccess(data.message || 'Бронирование успешно отменено');
                loadBookings();
            } else {
                const error = await response.json();
                showError(error.error || 'Не удалось отменить бронирование');
            }
        } catch (error) {
            console.error('Error cancelling booking:', error);
            showError('Произошла ошибка при отмене бронирования');
        }
    };

    /**
     * Открыть модальное окно редактирования
     */
    window.openEditModal = function(bookingId, checkIn, checkOut) {
        document.getElementById('edit-booking-id').value = bookingId;
        document.getElementById('edit-check-in').value = checkIn;
        document.getElementById('edit-check-out').value = checkOut;

        // Установка минимальной даты - сегодня
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('edit-check-in').min = today;
        document.getElementById('edit-check-out').min = today;

        editError.style.display = 'none';
        editModal.style.display = 'flex';
    };

    /**
     * Закрыть модальное окно
     */
    window.closeEditModal = function() {
        editModal.style.display = 'none';
        editForm.reset();
    };

    /**
     * Обработка отправки формы редактирования
     */
    async function handleEditSubmit(e) {
        e.preventDefault();
        editError.style.display = 'none';

        const bookingId = document.getElementById('edit-booking-id').value;
        const checkIn = document.getElementById('edit-check-in').value;
        const checkOut = document.getElementById('edit-check-out').value;

        // Валидация
        if (checkOut <= checkIn) {
            editError.textContent = 'Дата выезда должна быть позже даты заезда';
            editError.style.display = 'block';
            return;
        }

        try {
            const response = await API.updateBooking(bookingId, {
                check_in: checkIn,
                check_out: checkOut
            });

            if (response.ok) {
                closeEditModal();
                showSuccess('Бронирование успешно обновлено');
                loadBookings();
            } else {
                const error = await response.json();
                const errorMsg = error.room || error.check_in || error.check_out || error.detail || 'Не удалось обновить бронирование';
                editError.textContent = errorMsg;
                editError.style.display = 'block';
            }
        } catch (error) {
            console.error('Error updating booking:', error);
            editError.textContent = 'Произошла ошибка при обновлении';
            editError.style.display = 'block';
        }
    }

    /**
     * Сброс фильтров
     */
    function resetFilters() {
        statusFilter.value = '';
        timeFilter.value = '';
        sortFilter.value = '-created_at';
        loadBookings();
    }

    /**
     * Показать сообщение об ошибке
     */
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }

    /**
     * Показать сообщение об успехе
     */
    function showSuccess(message) {
        successMessage.textContent = message;
        successMessage.style.display = 'block';
        setTimeout(() => {
            successMessage.style.display = 'none';
        }, 5000);
    }

    /**
     * Форматирование даты
     */
    function formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    /**
     * Форматирование даты и времени
     */
    function formatDateTime(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Форматирование цены
     */
    function formatPrice(price) {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'KZT',
            minimumFractionDigits: 0
        }).format(price);
    }
});
