// static/js/script.js

document.addEventListener('DOMContentLoaded', function () {
    const logoUpload = document.getElementById('logoUpload');
    const logoList = document.getElementById('logoList');
    const logoError = document.getElementById('logoError');
    const excelUpload = document.getElementById('excelUpload');
    const excelList = document.getElementById('excelList');
    const excelError = document.getElementById('excelError');
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');

    if (!logoUpload || !logoList || !logoError || !excelUpload || !excelList || !excelError || !sidebar || !toggleBtn) return;

    let selectedLogos = [];
    let selectedExcel = null;

    // Manejar la selección de logos
    logoUpload.addEventListener('change', function (e) {
        const files = Array.from(e.target.files);

        for (let file of files) {
            if (file.size > 5 * 1024 * 1024) {
                showMessage('El archivo es demasiado grande. El tamaño máximo permitido es 5MB', true);
                return;
            }
            if (selectedLogos.length >= 10) {
                showMessage('Solo puedes subir hasta 10 logos.', true);
                break;
            }
            if (['image/png', 'image/jpeg', 'image/jpg'].includes(file.type)) {
                selectedLogos.push(file);
                displayLogo(file);
            } else {
                showMessage('Formato de logo no permitido.', true);
            }
        }
    });

    function createListItem(text, removeAction) {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.textContent = text;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-danger btn-sm';
        removeBtn.textContent = 'Eliminar';
        removeBtn.setAttribute('aria-label', 'Eliminar archivo');
        removeBtn.addEventListener('click', removeAction);

        li.appendChild(removeBtn);
        return li;
    }

    function displayLogo(file) {
        const li = createListItem(file.name, () => {
            selectedLogos = selectedLogos.filter((f) => f !== file);
            logoList.removeChild(li);
            logoError.style.display = 'none';
            updateLogoInput();
        });
        logoList.appendChild(li);
    }

    function updateLogoInput() {
        const dataTransfer = new DataTransfer();
        selectedLogos.forEach((file) => {
            dataTransfer.items.add(file);
        });
        logoUpload.files = dataTransfer.files;
    }

    // Manejar la selección de Excel
    excelUpload.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (selectedExcel) {
            showMessage('Solo se permite subir un archivo Excel a la vez.', true);
            excelUpload.value = ''; // Restablecer el input
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            showMessage('El archivo es demasiado grande. El tamaño máximo permitido es 5MB', true);
            return;
        }
        if (file && ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'].includes(file.type)) {
            selectedExcel = file;
            displayExcel(file);
        } else {
            showMessage('Formato de archivo Excel no permitido.', true);
        }
    });

    function displayExcel(file) {
        const li = createListItem(file.name, () => {
            selectedExcel = null;
            excelList.removeChild(li);
            excelError.style.display = 'none';
            excelUpload.value = ''; // Restablecer el input
        });
        excelList.appendChild(li);
    }

    // ** SIDEBAR TOGGLE **
    toggleBtn.addEventListener('click', function () {
        sidebar.classList.toggle('collapsed');
        this.innerHTML = sidebar.classList.contains('collapsed') ? 
            '<i class="bi bi-chevron-right"></i>' : 
            '<i class="bi bi-chevron-left"></i>';
    });
});

function showMessage(message, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${isError ? 'danger' : 'success'}`;
    messageDiv.textContent = message;
    const messageContainer = document.getElementById('messageContainer');
    if (messageContainer) {
        messageContainer.appendChild(messageDiv);
        setTimeout(() => messageDiv.remove(), 3000);
    }
}

// ** DATATABLES CONFIGURACIÓN **
$(document).ready(function () {
    $('.custom-datatable').DataTable({
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json",
        },
        pageLength: 10,
        lengthChange: true,
        ordering: true,
        searching: true,
    }).on('error.dt', function(e, settings, techNote, message) {
        console.error('DataTables Error: ', message);
        showMessage('Hubo un error al cargar la tabla de datos.', true);
    });
});