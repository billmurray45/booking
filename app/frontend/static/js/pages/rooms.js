/**
 * Rooms Page Script - Список комнат с фильтрацией
 */

document.addEventListener('DOMContentLoaded', function() {
    const roomsGrid = document.getElementById('rooms-grid');
    const loadingMessage = document.getElementById('loading-message');
    const errorMessage = document.getElementById('error-message');
    const emptyState = document.getElementById('empty-state');

    // Фильтры
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const capacitySelect = document.getElementById('capacity');
    const sortSelect = document.getElementById('sort');
    const applyFiltersBtn = document.getElementById('apply-filters');
    const resetFiltersBtn = document.getElementById('reset-filters');

    // Загрузка комнат при загрузке страницы
    loadRooms();

    // Обработчики событий
    applyFiltersBtn.addEventListener('click', loadRooms);
    resetFiltersBtn.addEventListener('click', resetFilters);

    // Загрузка при нажатии Enter в полях ввода
    minPriceInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') loadRooms();
    });
    maxPriceInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') loadRooms();
    });

    /**
     * Загрузка списка комнат
     */
    async function loadRooms() {
        // Скрываем все блоки
        roomsGrid.style.display = 'none';
        emptyState.style.display = 'none';
        errorMessage.style.display = 'none';
        loadingMessage.style.display = 'block';

        // Формируем URL с параметрами
        const url = buildRoomsUrl();

        try {
            const response = await fetch(url);

            if (response.ok) {
                const data = await response.json();
                displayRooms(data.results || data);
                loadingMessage.style.display = 'none';
            } else {
                throw new Error('Ошибка загрузки комнат');
            }
        } catch (error) {
            console.error('Error loading rooms:', error);
            loadingMessage.style.display = 'none';
            errorMessage.textContent = 'Не удалось загрузить комнаты. Попробуйте позже.';
            errorMessage.style.display = 'block';
        }
    }

    /**
     * Построение URL с параметрами фильтрации
     */
    function buildRoomsUrl() {
        const baseUrl = '/api/v1/rooms/';
        const params = new URLSearchParams();

        // Фильтр по минимальной цене
        if (minPriceInput.value) {
            params.append('min_price', minPriceInput.value);
        }

        // Фильтр по максимальной цене
        if (maxPriceInput.value) {
            params.append('max_price', maxPriceInput.value);
        }

        // Фильтр по вместимости
        if (capacitySelect.value) {
            params.append('capacity', capacitySelect.value);
        }

        // Сортировка
        if (sortSelect.value) {
            params.append('ordering', sortSelect.value);
        }

        return params.toString() ? `${baseUrl}?${params.toString()}` : baseUrl;
    }

    /**
     * Отображение списка комнат
     */
    function displayRooms(rooms) {
        // Очищаем сетку
        roomsGrid.innerHTML = '';

        if (!rooms || rooms.length === 0) {
            emptyState.style.display = 'block';
            roomsGrid.style.display = 'none';
            return;
        }

        // Создаем карточки комнат
        rooms.forEach(room => {
            const roomCard = createRoomCard(room);
            roomsGrid.appendChild(roomCard);
        });

        roomsGrid.style.display = 'grid';
    }

    /**
     * Создание карточки комнаты
     */
    function createRoomCard(room) {
        const card = document.createElement('a');
        card.href = `/rooms/${room.id}/`;
        card.className = 'room-card';

        // Изображение
        const imageUrl = room.image || '';
        const imagePlaceholder = imageUrl ? '' : 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="200"%3E%3Crect fill="%23f1f5f9" width="300" height="200"/%3E%3C/svg%3E';

        // Описание (обрезаем если длинное)
        const description = room.description
            ? (room.description.length > 100 ? room.description.substring(0, 100) + '...' : room.description)
            : 'Описание отсутствует';

        card.innerHTML = `
            <img src="${imageUrl || imagePlaceholder}" alt="${room.room_number}" class="room-card-image">
            <div class="room-card-body">
                <h3 class="room-card-title">Комната ${room.room_number}</h3>

                <div class="room-card-details">
                    <div class="room-card-detail">
                        <span class="room-card-detail-label">Вместимость:</span>
                        <span class="room-card-detail-value">${room.capacity} ${getPluralForm(room.capacity, 'человек', 'человека', 'человек')}</span>
                    </div>
                </div>

                <div class="room-card-price">
                    ${formatPrice(room.price_per_night)} <span class="room-card-price-label">/ ночь</span>
                </div>

                <p class="room-card-description">${description}</p>
            </div>
        `;

        return card;
    }

    /**
     * Сброс фильтров
     */
    function resetFilters() {
        minPriceInput.value = '';
        maxPriceInput.value = '';
        capacitySelect.value = '';
        sortSelect.value = 'room_number';
        loadRooms();
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
