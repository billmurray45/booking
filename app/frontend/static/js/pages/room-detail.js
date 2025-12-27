/**
 * Room Detail Page Script - Детальная информация о комнате
 */

document.addEventListener('DOMContentLoaded', function() {
    const loadingMessage = document.getElementById('loading-message');
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');
    const roomDetailContent = document.getElementById('room-detail-content');

    // Форма бронирования
    const bookingFormSection = document.getElementById('booking-form-section');
    const bookingForm = document.getElementById('booking-form');
    const loginPrompt = document.getElementById('login-prompt');
    const checkInInput = document.getElementById('check-in');
    const checkOutInput = document.getElementById('check-out');
    const bookingInfo = document.getElementById('booking-info');
    const bookingError = document.getElementById('booking-error');

    let currentRoom = null;

    // Получение ID комнаты из URL
    const roomId = getRoomIdFromUrl();

    if (!roomId) {
        showError('Неверный URL комнаты');
        return;
    }

    // Загрузка данных комнаты
    loadRoomDetail(roomId);

    // Установка минимальной даты - сегодня
    const today = new Date().toISOString().split('T')[0];
    checkInInput.min = today;
    checkOutInput.min = today;

    // Обработчики изменения дат
    checkInInput.addEventListener('change', calculateTotal);
    checkOutInput.addEventListener('change', calculateTotal);

    // Обработчик отправки формы
    if (bookingForm) {
        bookingForm.addEventListener('submit', handleBookingSubmit);
    }

    /**
     * Получение ID комнаты из URL
     */
    function getRoomIdFromUrl() {
        const path = window.location.pathname;
        const match = path.match(/\/rooms\/(\d+)\/?$/);
        return match ? match[1] : null;
    }

    /**
     * Загрузка детальной информации о комнате
     */
    async function loadRoomDetail(id) {
        // Показываем загрузку
        loadingMessage.style.display = 'block';
        roomDetailContent.style.display = 'none';
        errorMessage.style.display = 'none';

        const url = `/api/v1/rooms/${id}/`;

        try {
            const response = await fetch(url);

            if (response.ok) {
                const room = await response.json();
                displayRoomDetail(room);
                loadingMessage.style.display = 'none';
                roomDetailContent.style.display = 'block';
            } else if (response.status === 404) {
                throw new Error('Комната не найдена');
            } else {
                throw new Error('Ошибка загрузки информации о комнате');
            }
        } catch (error) {
            console.error('Error loading room detail:', error);
            showError(error.message || 'Не удалось загрузить информацию о комнате. Попробуйте позже.');
        }
    }

    /**
     * Отображение детальной информации о комнате
     */
    function displayRoomDetail(room) {
        currentRoom = room;

        // Изображение
        const roomImage = document.getElementById('room-image');
        if (room.image) {
            roomImage.src = room.image;
            roomImage.alt = `Комната ${room.room_number}`;
        } else {
            // SVG placeholder для комнаты без изображения
            roomImage.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="600" height="400"%3E%3Crect fill="%23f1f5f9" width="600" height="400"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="%23cbd5e1"%3E%D0%9D%D0%B5%D1%82 %D0%B8%D0%B7%D0%BE%D0%B1%D1%80%D0%B0%D0%B6%D0%B5%D0%BD%D0%B8%D1%8F%3C/text%3E%3C/svg%3E';
            roomImage.alt = 'Нет изображения';
        }

        // Заголовок
        document.getElementById('room-title').textContent = `Комната ${room.room_number}`;

        // Номер комнаты
        document.getElementById('room-number').textContent = room.room_number;

        // Цена
        document.getElementById('room-price').textContent = formatPrice(room.price_per_night);

        // Вместимость
        const capacityText = `${room.capacity} ${getPluralForm(room.capacity, 'человек', 'человека', 'человек')}`;
        document.getElementById('room-capacity').textContent = capacityText;

        // Статус
        const statusElement = document.getElementById('room-status');
        if (room.is_active) {
            statusElement.textContent = 'Доступна';
            statusElement.style.color = '#10b981'; // green
        } else {
            statusElement.textContent = 'Недоступна';
            statusElement.style.color = '#ef4444'; // red
        }

        // Описание
        const descriptionElement = document.getElementById('room-description');
        descriptionElement.textContent = room.description || 'Описание отсутствует';

        // Показать форму бронирования, если комната активна
        if (room.is_active) {
            showBookingForm();
        }
    }

    /**
     * Показать форму бронирования
     */
    function showBookingForm() {
        if (isAuthenticated()) {
            if (bookingForm) bookingForm.style.display = 'block';
            if (loginPrompt) loginPrompt.style.display = 'none';
        } else {
            if (bookingForm) bookingForm.style.display = 'none';
            if (loginPrompt) loginPrompt.style.display = 'block';
        }
        if (bookingFormSection) bookingFormSection.style.display = 'block';
    }

    /**
     * Расчет общей стоимости
     */
    function calculateTotal() {
        const checkIn = checkInInput.value;
        const checkOut = checkOutInput.value;

        if (!checkIn || !checkOut || !currentRoom) {
            bookingInfo.style.display = 'none';
            return;
        }

        const checkInDate = new Date(checkIn);
        const checkOutDate = new Date(checkOut);

        // Валидация дат
        if (checkOutDate <= checkInDate) {
            bookingInfo.style.display = 'none';
            return;
        }

        // Расчет количества ночей
        const nights = Math.ceil((checkOutDate - checkInDate) / (1000 * 60 * 60 * 24));
        const totalPrice = nights * currentRoom.price_per_night;

        // Отображение информации
        document.getElementById('nights-count').textContent = nights;
        document.getElementById('total-price').textContent = formatPrice(totalPrice);
        bookingInfo.style.display = 'block';
    }

    /**
     * Обработка отправки формы бронирования
     */
    async function handleBookingSubmit(e) {
        e.preventDefault();
        bookingError.style.display = 'none';
        errorMessage.style.display = 'none';

        const checkIn = checkInInput.value;
        const checkOut = checkOutInput.value;

        // Валидация
        if (!checkIn || !checkOut) {
            showBookingError('Пожалуйста, выберите даты заезда и выезда');
            return;
        }

        if (checkOut <= checkIn) {
            showBookingError('Дата выезда должна быть позже даты заезда');
            return;
        }

        try {
            const submitBtn = document.getElementById('submit-booking-btn');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Бронирование...';

            const response = await API.createBooking({
                room: currentRoom.id,
                check_in: checkIn,
                check_out: checkOut
            });

            if (response.ok) {
                const booking = await response.json();
                successMessage.textContent = `Бронирование успешно создано! Номер бронирования: #${booking.id}`;
                successMessage.style.display = 'block';

                // Очистка формы
                bookingForm.reset();
                bookingInfo.style.display = 'none';

                // Перенаправление на страницу бронирований через 2 секунды
                setTimeout(() => {
                    window.location.href = '/bookings/';
                }, 2000);
            } else {
                const error = await response.json();
                const errorMsg = error.room || error.check_in || error.check_out || error.detail || 'Не удалось создать бронирование';
                showBookingError(errorMsg);
                submitBtn.disabled = false;
                submitBtn.textContent = 'Забронировать';
            }
        } catch (error) {
            console.error('Error creating booking:', error);
            showBookingError('Произошла ошибка при создании бронирования');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Забронировать';
        }
    }

    /**
     * Показать ошибку бронирования
     */
    function showBookingError(message) {
        bookingError.textContent = message;
        bookingError.style.display = 'block';
    }

    /**
     * Отображение ошибки
     */
    function showError(message) {
        loadingMessage.style.display = 'none';
        roomDetailContent.style.display = 'none';
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
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

    /**
     * Получение правильной формы слова (человек/человека/человек)
     */
    function getPluralForm(number, one, few, many) {
        const mod10 = number % 10;
        const mod100 = number % 100;

        if (mod10 === 1 && mod100 !== 11) {
            return one;
        } else if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) {
            return few;
        } else {
            return many;
        }
    }
});
