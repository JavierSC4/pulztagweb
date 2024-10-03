// static/js/script.js
document.addEventListener('DOMContentLoaded', function () {
    const orderForm = document.getElementById('orderForm');

    // Logo Upload Elements
    const logoUpload = document.getElementById('logoUpload');
    const logoList = document.getElementById('logoList');
    const logoError = document.getElementById('logoError');
    let selectedLogos = [];

    // Excel Upload Elements
    const excelUpload = document.getElementById('excelUpload');
    const excelList = document.getElementById('excelList');
    const excelError = document.getElementById('excelError');
    let selectedExcel = null;

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
                displayLogo(file, selectedLogos.length - 1);
            }
        }
        logoUpload.value = ''; // Resetear el input
    });

    // Mostrar un logo en la lista
    function displayLogo(file, index) {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.textContent = file.name;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-danger btn-sm';
        removeBtn.textContent = 'Eliminar';
        removeBtn.addEventListener('click', function () {
            selectedLogos.splice(index, 1);
            logoList.removeChild(li);
            // Actualizar la lista
            updateLogoList();
            logoError.style.display = 'none';
        });

        li.appendChild(removeBtn);
        logoList.appendChild(li);
    }

    // Actualizar la lista de logos después de eliminar uno
    function updateLogoList() {
        logoList.innerHTML = '';
        selectedLogos.forEach((file, idx) => {
            displayLogo(file, idx);
        });
    }

    // Manejar la selección de Excel
    excelUpload.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (selectedExcel) {
            excelError.style.display = 'block';
            excelUpload.value = ''; // Resetear el input
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
        });

        li.appendChild(removeBtn);
        excelList.appendChild(li);
    }
});