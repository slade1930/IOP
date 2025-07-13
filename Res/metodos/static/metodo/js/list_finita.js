document.addEventListener('DOMContentLoaded', function() {
    // Inicialización de todos los componentes
    setupDetailToggles();
    setupFilters();
    setupDeleteButtons();
    setupGraphButtons();
    setupSearchFunctionality();
    setupTooltips();
});

// ========== FUNCIONES PRINCIPALES ==========

/**
 * Configura los botones para mostrar/ocultar detalles
 */
function setupDetailToggles() {
    document.querySelectorAll('.toggle-details').forEach(btn => {
        btn.addEventListener('click', function() {
            const details = this.closest('.result-item').querySelector('.details-content');
            const icon = this.querySelector('i');

            // Alternar visibilidad
            details.classList.toggle('hidden');
            
            // Alternar icono
            icon.classList.toggle('fa-chevron-down');
            icon.classList.toggle('fa-chevron-up');
            
            // Animación suave
            details.style.maxHeight = details.classList.contains('hidden') ? '0' : `${details.scrollHeight}px`;
        });
    });
}

/**
 * Configura los filtros por estado (todos, completados, fallidos)
 */
function setupFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.dataset.filter;

            // Actualizar botón activo
            document.querySelectorAll('.filter-btn').forEach(b => {
                b.classList.remove('active', 'bg-primary', 'text-white');
                b.classList.add('bg-gray-200', 'text-gray-700');
            });
            
            this.classList.add('active', 'bg-primary', 'text-white');
            this.classList.remove('bg-gray-200', 'text-gray-700');
            
            // Filtrar items
            document.querySelectorAll('.result-item').forEach(item => {
                if (filter === 'all') {
                    item.style.display = '';
                } else {
                    const matchesFilter = item.getAttribute('data-status') === filter;
                    item.style.display = matchesFilter ? '' : 'none';
                }
            });
        });
    });
}

/**
 * Configura los botones de eliminación con confirmación modal
 */
function setupDeleteButtons() {
    const deleteModal = document.getElementById('delete-modal');
    const cancelBtn = document.getElementById('cancel-delete');
    const confirmBtn = document.getElementById('confirm-delete');
    let currentItemToDelete = null;

    // Configurar clics en botones de borrado
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            currentItemToDelete = {
                id: this.dataset.id,
                url: this.dataset.url,
                element: this.closest('.result-item'),
                btn: this
            };
            
            // Deshabilitar botón durante la operación
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Procesando...';
            
            deleteModal.classList.remove('hidden');
        });
    });

    // Cancelar borrado
    cancelBtn.addEventListener('click', () => {
        if (currentItemToDelete) {
            currentItemToDelete.btn.disabled = false;
            currentItemToDelete.btn.innerHTML = '<i class="fas fa-trash-alt mr-1"></i> Borrar';
        }
        deleteModal.classList.add('hidden');
        currentItemToDelete = null;
    });

    // Confirmar borrado
    confirmBtn.addEventListener('click', async () => {
        if (!currentItemToDelete) return;
        
        deleteModal.classList.add('hidden');
        showToast('Eliminando cálculo...', 'info');
        
        try {
            const response = await fetch(currentItemToDelete.url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await handleResponse(response);

            if (data.success) {
                animateRemoval(currentItemToDelete.element);
                showToast('Cálculo eliminado correctamente', 'success');
                
                // Actualizar contador si existe
                updateCounter();
            } else {
                throw new Error(data.error || 'Error al eliminar el cálculo');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast(error.message || 'Error en el servidor', 'error');
            
            // Restaurar botón si falla
            if (currentItemToDelete.btn) {
                currentItemToDelete.btn.disabled = false;
                currentItemToDelete.btn.innerHTML = '<i class="fas fa-trash-alt mr-1"></i> Borrar';
            }
        } finally {
            currentItemToDelete = null;
        }
    });
}

/**
 * Configura los botones para mostrar gráficas
 */
function setupGraphButtons() {
    const graphModal = document.getElementById('graph-modal');
    const graphImage = document.getElementById('graph-image');
    const closeBtn = document.getElementById('close-graph');

    document.querySelectorAll('.show-graph-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const graphData = btn.dataset.graph;
            if (graphData) {
                graphImage.src = `data:image/png;base64,${graphData}`;
                graphModal.classList.remove('hidden');
                document.body.style.overflow = 'hidden'; // Bloquear scroll
            } else {
                showToast('Gráfico no disponible para este cálculo', 'warning');
            }
        });
    });

    // Cerrar modal
    const closeModal = () => {
        graphModal.classList.add('hidden');
        document.body.style.overflow = ''; // Restaurar scroll
    };

    closeBtn.addEventListener('click', closeModal);
    graphModal.addEventListener('click', (e) => {
        if (e.target === graphModal) closeModal();
    });

    // Cerrar con ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !graphModal.classList.contains('hidden')) {
            closeModal();
        }
    });
}

/**
 * Configura la funcionalidad de búsqueda
 */
function setupSearchFunctionality() {
    const searchInput = document.querySelector('input[type="text"][placeholder="Buscar función..."]');
    if (!searchInput) return;

    searchInput.addEventListener('input', debounce(() => {
        const searchTerm = searchInput.value.toLowerCase();
        
        document.querySelectorAll('.result-item').forEach(item => {
            const functionText = item.querySelector('h3').textContent.toLowerCase();
            const matchesSearch = functionText.includes(searchTerm);
            item.style.display = matchesSearch ? '' : 'none';
        });
    }, 300));
}

/**
 * Configura tooltips para elementos interactivos
 */
function setupTooltips() {
    tippy('[data-tippy-content]', {
        arrow: true,
        animation: 'fade',
        duration: [200, 150],
        delay: [100, 0],
    });
}

// ========== FUNCIONES AUXILIARES ==========

/**
 * Animación al eliminar un elemento
 */
function animateRemoval(element) {
    if (!element) return;
    
    element.style.opacity = '0';
    element.style.transform = 'translateX(100px)';
    element.style.transition = 'all 0.3s ease';
    
    setTimeout(() => {
        element.remove();
        checkEmptyState();
    }, 300);
}

/**
 * Muestra notificaciones toast
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || document.body;
    const toast = document.createElement('div');
    
    const typeConfig = {
        success: { icon: 'fa-check-circle', color: 'bg-green-500' },
        error: { icon: 'fa-exclamation-circle', color: 'bg-red-500' },
        warning: { icon: 'fa-exclamation-triangle', color: 'bg-yellow-500' },
        info: { icon: 'fa-info-circle', color: 'bg-blue-500' }
    };
    
    const config = typeConfig[type] || typeConfig.info;
    
    toast.className = `${config.color} text-white px-4 py-3 rounded-md shadow-lg flex items-center mb-2 transform transition-all duration-300 ease-out`;
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(20px)';
    toast.innerHTML = `
        <i class="fas ${config.icon} mr-2"></i>
        <span>${message}</span>
    `;
    
    container.prepend(toast);
    
    // Animación de entrada
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    }, 10);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

/**
 * Verifica si no hay elementos y muestra estado vacío
 */
function checkEmptyState() {
    const emptyState = document.querySelector('.empty-state');
    const items = document.querySelectorAll('.result-item');
    
    if (items.length === 0) {
        if (!emptyState) {
            window.location.reload(); // Recargar para mostrar estado vacío completo
        }
    }
}

/**
 * Actualiza el contador de cálculos
 */
function updateCounter() {
    const counterElement = document.querySelector('.calculations-counter');
    if (counterElement) {
        const currentCount = parseInt(counterElement.textContent) || 0;
        counterElement.textContent = Math.max(0, currentCount - 1);
    }
}

/**
 * Obtiene el token CSRF
 */
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

/**
 * Maneja la respuesta del servidor
 */
function handleResponse(response) {
    if (!response.ok) {
        return response.text().then(text => {
            throw new Error(text || `HTTP error! status: ${response.status}`);
        });
    }
    return response.json();
}

/**
 * Debounce para eventos de búsqueda
 */
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// ========== POLYFILLS ==========

// Polyfill para closest() en Edge
if (!Element.prototype.matches) {
    Element.prototype.matches = Element.prototype.msMatchesSelector;
}

if (!Element.prototype.closest) {
    Element.prototype.closest = function(s) {
        let el = this;
        do {
            if (el.matches(s)) return el;
            el = el.parentElement || el.parentNode;
        } while (el !== null && el.nodeType === 1);
        return null;
    };
}