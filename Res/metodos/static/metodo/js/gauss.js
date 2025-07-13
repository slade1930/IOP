// Insertar ejemplos
document.querySelectorAll('.example-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.getElementById('id_matriz_a').value = this.getAttribute('data-matrix');
        document.getElementById('id_vector_b').value = this.getAttribute('data-vector');
    });
});

// Validación de matriz (simplificada)
document.getElementById('validate-matrix').addEventListener('click', function() {
    const matrixInput = document.getElementById('id_matriz_a');
    const validationPanel = document.getElementById('validation-result');
    const validationMsg = document.getElementById('validation-message');

    try {
        const matrix = JSON.parse(matrixInput.value);
        if (Array.isArray(matrix) && matrix.every(row => Array.isArray(row))) {
            validationPanel.classList.remove('hidden', 'bg-red-50', 'text-red-800');
            validationPanel.classList.add('bg-green-50', 'text-green-800');
            validationMsg.innerHTML = '<i class="fas fa-check-circle mr-1"></i> La matriz tiene formato válido';
        } else {
            throw new Error('Formato incorrecto');
        }
    } catch (e) {
        validationPanel.classList.remove('hidden', 'bg-green-50', 'text-green-800');
        validationPanel.classList.add('bg-red-50', 'text-red-800');
        validationMsg.innerHTML = '<i class="fas fa-exclamation-circle mr-1"></i> Formato JSON inválido para matriz';
    }
    validationPanel.classList.remove('hidden');
});

// Validación en tiempo real de JSON
document.getElementById('id_matriz_a').addEventListener('input', function() {
    const validationPanel = document.getElementById('validation-result');
    validationPanel.classList.add('hidden');
});

document.getElementById('id_vector_b').addEventListener('input', function() {
    const validationPanel = document.getElementById('validation-result');
    validationPanel.classList.add('hidden');
});