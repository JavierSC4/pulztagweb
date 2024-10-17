  hello

  <!-- Información Bancaria Section -->
<div class="row justify-content-center mt-5">
    <div class="col-md-8">
        <div class="custom-solutions-section text-center p-5 rounded shadow">
            <h4 class="text-white">Datos para Transferencia</h4>
            <ul class="list-unstyled">
                <li><strong>Banco:</strong> Banco de Chile</li>
                <li><strong>Tipo de Cuenta:</strong> Cuenta Corriente</li>
                <li><strong>Nombre:</strong> Pulztag SpA</li>
                <li><strong>Número de Cuenta:</strong> 00-888-08888-08</li>
                <li><strong>RUT:</strong> 88.888.888-8</li>
                <li><strong>Correo:</strong> <a href="mailto:contacto@pulztag.com" class="text-white">contacto@pulztag.com</a></li>
                <li><strong>Teléfono:</strong> <a href="tel:+56962411963" class="text-white">+56962411963</a></li>
            </ul>
        </div>
    </div>
</div>


<!-- templates/order.html -->
{% extends 'base.html' %}

{% block title %}Pedido - PulztagWeb{% endblock %}

{% block content %}
<h2 class="text-center mb-4">Realiza tu Pedido</h2>
<p class="text-center mb-5">Completa el formulario a continuación para realizar tu pedido de dispositivos NFC
    personalizados.</p>

<!-- Mensajes Flash -->
{% with messages = get_flashed_messages(with_categories=true) %}
{% if messages %}
<div class="row justify-content-center">
    <div class="col-md-8">
        {% for category, message in messages %}
        <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
        </div>
        {% endfor %}
    </div>
</div>
{% endif %}
{% endwith %}

<div class="row justify-content-center">
    <div class="col-md-8 mb-4">
        <form method="POST" action="{{ url_for('order') }}" enctype="multipart/form-data" id="orderForm">
            <!-- Campos del formulario -->
            <div class="mb-3">
                <label for="nombre" class="form-label">Nombre</label>
                <input type="text" class="form-control" id="nombre" name="nombre" placeholder="Tu nombre" required>
            </div>
            <div class="mb-3">
                <label for="email" class="form-label">Correo Electrónico</label>
                <input type="email" class="form-control" id="email" name="email" placeholder="nombre@ejemplo.com"
                    required>
            </div>
            <div class="mb-3">
                <label for="dispositivo" class="form-label">Selecciona un Dispositivo</label>
                <select class="form-select" id="dispositivo" name="dispositivo" required>
                    <option value="" disabled selected>Elige una opción</option>
                    <option value="NFC Token de PVC (30 mm)">NFC Token de PVC (30 mm)</option>
                    <option value="NFC Sticker (25 mm)">NFC Sticker (25 mm)</option>
                    <option value="NFC Cards">NFC Cards</option>
                    <!-- Agrega más opciones según sea necesario -->
                </select>
            </div>
            <div class="mb-3">
                <label for="mensaje" class="form-label">¿Qué necesitas?</label>
                <textarea class="form-control" id="mensaje" name="mensaje" rows="3"
                    placeholder="Escribe tu mensaje aquí" required></textarea>
            </div>

<!-- Sección para subir Logos -->
            <div class="mb-4">
                <label class="form-label">Subir Logos (png, jpeg, jpg) - Máximo 10 (*)</label>
                <input type="file" class="form-control" id="logoUpload" name="logos" accept=".png, .jpeg, .jpg" multiple>
                <ul class="list-group mt-2" id="logoList"></ul>
                <div id="logoError" class="text-danger mt-2" style="display: none;">Has alcanzado el máximo de 10 logos.</div>
                <p class="text-muted mt-2">(*) Sube aquí las imágenes que deseas imprimir en tus dispositivos personalizados. Nuestro equipo se encargará de ayudarte con la implementación y asegurará que tus diseños se vean espectaculares en cada producto.</p>
            </div>

            <!-- Sección para subir Archivo Excel -->
            <div class="mb-4">
                <label class="form-label">Subir Archivo Excel (xlsx, xls) - Máximo 1 (*)</label>
                <input type="file" class="form-control" id="excelUpload" name="excel" accept=".xlsx, .xls">
                <ul class="list-group mt-2" id="excelList"></ul>
                <div id="excelError" class="text-danger mt-2" style="display: none;">Solo puedes subir un archivo Excel.</div>
                <p class="text-muted mt-2">(*) Cada dispositivo puede tener una configuración única. Para pedidos de gran volumen, por favor proporciona los detalles en un archivo Excel. Así, podremos garantizar que cada dispositivo se ajuste a tus necesidades específicas.</p>
            </div>
            <button type="submit" class="btn btn-primary">Enviar solicitud</button>
        </form>
    </div>
</div>