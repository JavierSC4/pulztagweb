document.addEventListener('DOMContentLoaded', function () {
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
                displayLogo(file);
            }
        }
        // No restablezcas el valor del input
        // logoUpload.value = ''; // Comentado para permitir que los archivos se envíen
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
            // Eliminar el archivo de selectedLogos
            selectedLogos = selectedLogos.filter((f) => f !== file);
            logoList.removeChild(li);
            logoError.style.display = 'none';

            // Actualizar el input de archivos
            updateLogoInput();
        });

        li.appendChild(removeBtn);
        logoList.appendChild(li);
    }

    // Actualizar el input de archivos para reflejar los archivos seleccionados
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
            excelError.style.display = 'block';
            // Restablece el input para evitar múltiples archivos
            excelUpload.value = '';
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
});