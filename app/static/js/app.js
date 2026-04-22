document.addEventListener('DOMContentLoaded', function() {
    initModals();
    initConfirmDelete();
    initFlashMessages();
    initObjectSelection();
});

function initModals() {
    document.querySelectorAll('[data-modal]').forEach(trigger => {
        trigger.addEventListener('click', () => {
            const modalId = trigger.dataset.modal;
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('active');
            }
        });
    });

    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal').classList.remove('active');
        });
    });

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
}

function initConfirmDelete() {
    document.querySelectorAll('[data-confirm]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const message = btn.dataset.confirm || 'Вы уверены?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

function initFlashMessages() {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 300);
        }, 3000);
    });
}

function initObjectSelection() {
    const objectCards = document.querySelectorAll('.object-select-card');
    objectCards.forEach(card => {
        card.addEventListener('click', () => {
            const checkbox = card.querySelector('input[type="checkbox"]');
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                card.classList.toggle('selected', checkbox.checked);
            }
        });
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

function showFlash(message, type = 'success') {
    const container = document.querySelector('.flash-messages') || createFlashContainer();
    const flash = document.createElement('div');
    flash.className = `flash flash-${type}`;
    flash.textContent = message;
    container.appendChild(flash);
    
    setTimeout(() => {
        flash.style.opacity = '0';
        setTimeout(() => flash.remove(), 300);
    }, 3000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.querySelector('.main .container').prepend(container);
    return container;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showFlash('Скопировано в буфер обмена');
    }).catch(() => {
        showFlash('Не удалось скопировать', 'error');
    });
}