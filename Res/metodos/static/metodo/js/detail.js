// Función para manejar el toggle de detalles
function setupDetailToggles() {
    document.querySelectorAll('.toggle-details').forEach(btn => {
        btn.addEventListener('click', function() {
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
        btn.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');

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
                    if (item.getAttribute('data-status') === filter) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                }
            });
        });
    });
}

// Función para manejar el borrado de elementos
function setupDeleteButtons() {
    let itemToDelete = null;
    const deleteModal = document.getElementById('delete-modal');
    const cancelDeleteBtn = document.getElementById('cancel-delete');
    const confirmDeleteBtn = document.getElementById('confirm-delete');

    // Mostrar modal al hacer clic en borrar
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            itemToDelete = this.getAttribute('data-id');
            deleteModal.classList.remove('hidden');
        });
    });

    // Cancelar borrado
    cancelDeleteBtn.addEventListener('click', function() {
        deleteModal.classList.add('hidden');
        itemToDelete = null;
    });

    // Confirmar borrado
    confirmDeleteBtn.addEventListener('click', function() {
        if (itemToDelete) {
            fetch(`/gauss-eliminacion/eliminar/${itemToDelete}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({}) // Cuerpo vacío pero necesario para POST
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Eliminar el elemento del DOM
                    const itemElement = document.querySelector(`.result-item[data-id="${itemToDelete}"]`);
                    if (itemElement) {
                        itemElement.remove();
                        showToast('Cálculo eliminado correctamente', 'success');
                        
                        // Si no quedan elementos, recargar la página
                        if (document.querySelectorAll('.result-item').length === 0) {
                            setTimeout(() => {
                                window.location.reload();
                            }, 1500);
                        }
                    }
                } else {
                    throw new Error(data.error || 'Error al eliminar el cálculo');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast(error.message || 'Error al comunicarse con el servidor', 'error');
            })
            .finally(() => {
                deleteModal.classList.add('hidden');
                itemToDelete = null;
            });
        }
    });
}

// Función para manejar la visualización de gráficas
function setupGraphButtons() {
    const graphModal = document.getElementById('graph-modal');
    const graphImage = document.getElementById('graph-image');
    const closeGraphBtn = document.getElementById('close-graph');

    // Mostrar gráfica al hacer clic
    document.querySelectorAll('.show-graph-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const graphData = this.getAttribute('data-graph');
            if (graphData) {
                graphImage.src = `data:image/png;base64,${graphData}`;
                graphModal.classList.remove('hidden');
            } else {
                showToast('No hay gráfica disponible para este cálculo', 'error');
            }
        });
    });

    // Cerrar modal
    closeGraphBtn.addEventListener('click', () => {
        graphModal.classList.add('hidden');
    });

    // Cerrar al hacer clic fuera de la imagen
    graphModal.addEventListener('click', (e) => {
        if (e.target === graphModal) {
            graphModal.classList.add('hidden');
        }
    });
}

// Función para mostrar notificaciones toast
function showToast(message, type) {
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast fixed top-4 right-4 z-50';

    const toast = document.createElement('div');
    toast.className = `px-6 py-3 rounded-md text-white ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } shadow-lg flex items-center`;

    const icon = document.createElement('i');
    icon.className = type === 'success' ? 'fas fa-check-circle mr-2' : 'fas fa-exclamation-circle mr-2';

    const text = document.createElement('span');
    text.textContent = message;

    toast.appendChild(icon);
    toast.appendChild(text);
    toastContainer.appendChild(toast);
    document.body.appendChild(toastContainer);

    // Eliminar después de 3 segundos
    setTimeout(() => {
        toastContainer.remove();
    }, 3000);
}

// Función para obtener cookie CSRF
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

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    setupDetailToggles();
    setupFilters();
    setupDeleteButtons();
    setupGraphButtons();
});

document.addEventListener('DOMContentLoaded', function() {
  // Resaltar la solución óptima en las tablas
  const highlightSolution = (table) => {
    const rows = table.querySelectorAll('tbody tr');
    if (rows.length > 0) {
      const lastRow = rows[rows.length - 1];
      const cells = lastRow.querySelectorAll('td');
      if (cells.length > 0) {
        cells[cells.length - 1].classList.add('font-bold', 'text-green-800');
      }
    }
  };

  document.querySelectorAll('table').forEach(highlightSolution);

  // Agregar tooltips para las variables básicas
  tippy('[data-tippy-content]', {
    allowHTML: true,
    placement: 'top',
    interactive: true,
  });
});