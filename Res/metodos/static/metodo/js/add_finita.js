document.addEventListener('DOMContentLoaded', function() {
    // Configurar botones de ejemplo
    setupExampleButtons();
    
    // Configurar validación de función
    setupFunctionValidation();
});

// Función para configurar los botones de ejemplo
function setupExampleButtons() {
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Insertar función
            document.getElementById('id_funcion').value = this.getAttribute('data-funcion');
            
            // Insertar punto
            document.getElementById('id_punto').value = this.getAttribute('data-punto');
            
            // Insertar tamaño de paso h
            document.getElementById('id_h').value = this.getAttribute('data-h');
            
            // Insertar orden
            document.getElementById('id_orden').value = this.getAttribute('data-orden');
            
            // Insertar tipo
            document.getElementById('id_tipo').value = this.getAttribute('data-tipo');
            
            // Mostrar mensaje de éxito
            showValidationMessage('Ejemplo cargado correctamente', 'success');
        });
    });
}

// Función para configurar la validación de la función matemática
function setupFunctionValidation() {
    const validateBtn = document.getElementById('validate-function');
    if (validateBtn) {
        validateBtn.addEventListener('click', validateFunction);
    }
}

// Función para validar la función matemática
function validateFunction() {
    const functionInput = document.getElementById('id_funcion');
    const pointInput = document.getElementById('id_punto');
    const hInput = document.getElementById('id_h');
    const validationPanel = document.getElementById('validation-result');
    
    try {
        // Validar que la función no esté vacía
        if (!functionInput.value.trim()) {
            throw new Error('La función no puede estar vacía');
        }
        
        // Validar que contenga la variable x
        if (!functionInput.value.includes('x')) {
            throw new Error('La función debe contener la variable x');
        }
        
        // Validar punto numérico
        if (isNaN(parseFloat(pointInput.value))) {
            throw new Error('El punto debe ser un número válido');
        }
        
        // Validar h positivo
        const h = parseFloat(hInput.value);
        if (isNaN(h) || h <= 0) {
            throw new Error('El tamaño de paso h debe ser un número positivo');
        }
        
        // Mostrar mensaje de éxito
        showValidationMessage('La función y parámetros son válidos', 'success');
        
    } catch (error) {
        // Mostrar mensaje de error
        showValidationMessage(`Error: ${error.message}`, 'error');
    }
}

// Función para mostrar mensajes de validación
function showValidationMessage(message, type) {
    const validationPanel = document.getElementById('validation-result');
    const validationMsg = document.getElementById('validation-message');
    
    validationPanel.classList.remove('hidden');
    
    if (type === 'success') {
        validationPanel.classList.remove('bg-red-50', 'text-red-800');
        validationPanel.classList.add('bg-green-50', 'text-green-800');
        validationMsg.innerHTML = `<i class="fas fa-check-circle mr-2"></i>${message}`;
    } else {
        validationPanel.classList.remove('bg-green-50', 'text-green-800');
        validationPanel.classList.add('bg-red-50', 'text-red-800');
        validationMsg.innerHTML = `<i class="fas fa-exclamation-circle mr-2"></i>${message}`;
    }
    
    // Desplazarse al panel de validación
    validationPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Validación en tiempo real mientras se escribe
document.getElementById('id_funcion')?.addEventListener('input', function() {
    // Validación básica de la función
    if (this.value.includes('x')) {
        this.classList.remove('border-red-500');
        this.classList.add('border-green-500');
    } else {
        this.classList.remove('border-green-500');
        this.classList.add('border-red-500');
    }
});

// Validación del punto
document.getElementById('id_punto')?.addEventListener('input', function() {
    if (!isNaN(parseFloat(this.value))) {  // Faltaba este paréntesis de cierre
        this.classList.remove('border-red-500');
        this.classList.add('border-green-500');
    } else {
        this.classList.remove('border-green-500');
        this.classList.add('border-red-500');
    }
});

// Validación de h
document.getElementById('id_h')?.addEventListener('input', function() {
    const h = parseFloat(this.value);
    if (!isNaN(h) && h > 0) {
        this.classList.remove('border-red-500');
        this.classList.add('border-green-500');
    } else {
        this.classList.remove('border-green-500');
        this.classList.add('border-red-500');
    }
});

// Validación del formulario al enviar
document.getElementById('calculation-form')?.addEventListener('submit', function(e) {
    const functionInput = document.getElementById('id_funcion');
    const pointInput = document.getElementById('id_punto');
    const hInput = document.getElementById('id_h');
    
    let isValid = true;
    
    // Validar función
    if (!functionInput.value.includes('x')) {
        functionInput.classList.add('border-red-500');
        isValid = false;
    }
    
    // Validar punto
    if (isNaN(parseFloat(pointInput.value))) {
        pointInput.classList.add('border-red-500');
        isValid = false;
    }
    
    // Validar h
    const h = parseFloat(hInput.value);
    if (isNaN(h) || h <= 0) {
        hInput.classList.add('border-red-500');
        isValid = false;
    }
    
    if (!isValid) {
        e.preventDefault();
        showValidationMessage('Por favor corrige los errores en el formulario', 'error');
    }
});