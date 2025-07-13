// Función para manejar el toggle de detalles
function setupDetailToggles() {
    document.querySelectorAll('.toggle-details').forEach(btn => {
        btn.addEventListener('click', function () {
            const details = this.closest('.result-item').querySelector('.details-content');
            const icon = this.querySelector('i');

            details.classList.toggle('hidden');
            icon.classList.toggle('fa-chevron-down');
            icon.classList.toggle('fa-chevron-up');
        });
    });
}

// Función para manejar los filtros
function setupFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const filter = this.getAttribute('data-filter');

            document.querySelectorAll('.filter-btn').forEach(b => {
                b.classList.remove('active', 'bg-primary', 'text-white');
                b.classList.add('bg-gray-200', 'text-gray-700');
            });

            this.classList.add('active', 'bg-primary', 'text-white');
            this.classList.remove('bg-gray-200', 'text-gray-700');

            document.querySelectorAll('.result-item').forEach(item => {
                if (filter === 'all') {
                    item.style.display = '';
                } else {
                    item.style.display = (item.getAttribute('data-status') === filter) ? '' : 'none';
                }
            });
        });
    });
}

// Función para manejar la visualización de gráficas
function setupGraphButtons() {
    const graphModal = document.getElementById('graph-modal');
    const graphImage = document.getElementById('graph-image');
    const closeGraphBtn = document.getElementById('close-graph');

    document.querySelectorAll('.show-graph-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const graphData = this.getAttribute('data-graph');
            if (graphData) {
                graphImage.src = `data:image/png;base64,${graphData}`;
                graphModal.classList.remove('hidden');
            } else {
                showToast('No hay gráfica disponible para este cálculo', 'error');
            }
        });
    });

    closeGraphBtn.addEventListener('click', () => {
        graphModal.classList.add('hidden');
    });

    graphModal.addEventListener('click', (e) => {
        if (e.target === graphModal) {
            graphModal.classList.add('hidden');
        }
    });
}

// Función para manejar el borrado con modal (VERSIÓN MODIFICADA)
function setupDeleteButtons() {
    let itemToDeleteId = null;
    const deleteModal = document.getElementById('delete-modal');
    const cancelDeleteBtn = document.getElementById('cancel-delete');
    const confirmDeleteBtn = document.getElementById('confirm-delete');

    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            itemToDeleteId = this.getAttribute('data-id');
            deleteModal.classList.remove('hidden');
        });
    });

    cancelDeleteBtn.addEventListener('click', function () {
        deleteModal.classList.add('hidden');
        itemToDeleteId = null;
    });

    confirmDeleteBtn.addEventListener('click', function () {
        if (itemToDeleteId) {
            fetch(`/falsa-posicion/eliminar/${itemToDeleteId}/`, {  // Esta URL debe coincidir con tu urls.py
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    const itemElement = document.querySelector(`.result-item[data-id="${itemToDeleteId}"]`);
                    if (itemElement) {
                        itemElement.remove();
                        showToast('Cálculo eliminado correctamente', 'success');

                        // Recargar si no quedan elementos
                        if (document.querySelectorAll('.result-item').length === 0) {
                            window.location.reload();
                        }
                    }
                } else {
                    showToast(data.error || 'Error al eliminar el cálculo', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error al comunicarse con el servidor', 'error');
            })
            .finally(() => {
                deleteModal.classList.add('hidden');
                itemToDeleteId = null;
            });
        }
    });
}

// Función para mostrar toasts
function showToast(message, type) {
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast fixed top-4 right-4 z-50';

    const toast = document.createElement('div');
    toast.className = `px-6 py-3 rounded-md text-white ${type === 'success' ? 'bg-green-500' : 'bg-red-500'} shadow-lg flex items-center`;

    const icon = document.createElement('i');
    icon.className = type === 'success' ? 'fas fa-check-circle mr-2' : 'fas fa-exclamation-circle mr-2';

    const text = document.createElement('span');
    text.textContent = message;

    toast.appendChild(icon);
    toast.appendChild(text);
    toastContainer.appendChild(toast);
    document.body.appendChild(toastContainer);

    setTimeout(() => {
        toastContainer.remove();
    }, 3000);
}

// Función para obtener CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Inicializar todo
document.addEventListener('DOMContentLoaded', function () {
    setupDetailToggles();
    setupFilters();
    setupDeleteButtons();
    setupGraphButtons();
});