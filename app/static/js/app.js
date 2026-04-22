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

function generatePrompt() {
    const templateId = document.querySelector('[name="template_id"]').value;
    const selectedObjects = Array.from(document.querySelectorAll('.object-select-card input:checked'))
        .map(cb => ({
            object_id: cb.value,
            custom_text: ''
        }));
    
    if (!templateId) {
        showFlash('Выберите шаблон', 'error');
        return;
    }
    
    fetch('/api/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            template_id: templateId,
            items: selectedObjects
        })
    })
    .then(response => response.json())
    .then(data => {
        const promptDisplay = document.getElementById('generated-prompt');
        if (promptDisplay) {
            promptDisplay.textContent = data.generated_prompt;
        }
        showFlash('Промт сгенерирован');
    })
    .catch(error => {
        showFlash('Ошибка генерации', 'error');
    });
}

async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const response = await fetch(endpoint, { ...defaultOptions, ...options });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
}

async function loadCategoryObjects(categoryId) {
    try {
        const objects = await apiRequest(`/api/objects?category_id=${categoryId}`);
        renderObjectsList(objects);
    } catch (error) {
        showFlash('Ошибка загрузки объектов', 'error');
    }
}

function renderObjectsList(objects) {
    const container = document.getElementById('objects-list');
    if (!container) return;
    
    if (objects.length === 0) {
        container.innerHTML = '<p class="empty-state">Объектов пока нет</p>';
        return;
    }
    
    container.innerHTML = objects.map(obj => `
        <div class="object-card" data-id="${obj.id}">
            ${obj.image_path ? `<img src="${obj.image_path}" class="object-card-image" alt="${obj.name}">` : ''}
            <div class="object-card-content">
                <div class="object-card-title">${obj.name}</div>
                <div class="object-card-prompt">${obj.prompt}</div>
            </div>
            <div class="actions">
                <a href="/objects/edit/${obj.id}" class="btn btn-sm btn-secondary">Ред.</a>
                <a href="/objects/delete/${obj.id}" class="btn btn-sm btn-danger" data-confirm="Удалить объект?">Удал.</a>
            </div>
        </div>
    `).join('');
}