document.addEventListener('DOMContentLoaded', function () {
    // ** LOGO UPLOAD **
    const logoUpload = document.getElementById('logoUpload');
    const logoList = document.getElementById('logoList');
    const logoError = document.getElementById('logoError');
    let selectedLogos = [];

    // Manejar la selección de logos
    logoUpload.addEventListener('change', function (e) {
        const files = Array.from(e.target.files);

        for (let file of files) {
            if (selectedLogos.length >= 10) {
                logoError.style.display = 'block';
                break;
            }
            if (['image/png', 'image/jpeg', 'image/jpg'].includes(file.type)) {
                selectedLogos.push(file);
                displayLogo(file);
            }
        }
    });

    // Mostrar un logo en la lista
    function displayLogo(file) {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.textContent = file.name;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-danger btn-sm';
        removeBtn.textContent = 'Eliminar';
        removeBtn.addEventListener('click', function () {
            selectedLogos = selectedLogos.filter((f) => f !== file);
            logoList.removeChild(li);
            logoError.style.display = 'none';
            updateLogoInput();
        });

        li.appendChild(removeBtn);
        logoList.appendChild(li);
    }

    // Actualizar el input de archivos para reflejar los logos seleccionados
    function updateLogoInput() {
        const dataTransfer = new DataTransfer();
        selectedLogos.forEach((file) => {
            dataTransfer.items.add(file);
        });
        logoUpload.files = dataTransfer.files;
    }

    // ** EXCEL UPLOAD **
    const excelUpload = document.getElementById('excelUpload');
    const excelList = document.getElementById('excelList');
    const excelError = document.getElementById('excelError');
    let selectedExcel = null;

    // Manejar la selección de Excel
    excelUpload.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (selectedExcel) {
            excelError.style.display = 'block';
            excelUpload.value = ''; // Restablecer el input
            return;
        }
        if (file && ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'].includes(file.type)) {
            selectedExcel = file;
            displayExcel(file);
        }
    });

    // Mostrar el archivo Excel en la lista
    function displayExcel(file) {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.textContent = file.name;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-danger btn-sm';
        removeBtn.textContent = 'Eliminar';
        removeBtn.addEventListener('click', function () {
            selectedExcel = null;
            excelList.removeChild(li);
            excelError.style.display = 'none';
            excelUpload.value = ''; // Restablecer el input
        });

        li.appendChild(removeBtn);
        excelList.appendChild(li);
    }

    // ** SIDEBAR TOGGLE **
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');

    toggleBtn.addEventListener('click', function () {
        sidebar.classList.toggle('collapsed'); // Alterna la clase 'collapsed'
        if (sidebar.classList.contains('collapsed')) {
            this.innerHTML = '<i class="bi bi-chevron-right"></i>'; // Cambia el ícono al colapsar
        } else {
            this.innerHTML = '<i class="bi bi-chevron-left"></i>'; // Cambia el ícono al expandir
        }
    });
});

// ** DATATABLES CONFIGURACIÓN **
$(document).ready(function () {
    $('.custom-datatable').DataTable({
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json", // Español
        },
        pageLength: 10,
        lengthChange: true,
        ordering: true,
        searching: true,
    });
});