< !--templates / base.html-- >

< !DOCTYPE html >
    <html lang="es">

        <head>
            <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{% block title %}Pulztag{% endblock %}</title>

                    <!-- Google Fonts -->
                    <link
                        href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700&family=Roboto:wght@400;500&display=swap"
                        rel="stylesheet">

                        <!-- Bootstrap CSS -->
                        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

                            <!-- Bootstrap Icons -->
                            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">

                                <!-- CSS Personalizado con Parámetro de Versión para Evitar Caché -->
                                <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}?v=1.0">

                                    {% block head %}{% endblock %}
                                </head>

                                <body>
                                    <!-- Barra Superior -->
                                    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
                                        <div class="container-fluid">
                                            <!-- Marca de la Navbar -->
                                            <a class="navbar-brand text-primary fw-bold" href="/">
                                                <!-- Puedes agregar un logo aquí si lo deseas -->
                                                <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Pulztag Logo" height="40">
                                            </a>
                                            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                                                aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                                                <span class="navbar-toggler-icon"></span>
                                            </button>
                                            <!-- Enlaces de Navegación -->
                                            <div class="collapse navbar-collapse" id="navbarNav">
                                                <ul class="navbar-nav ms-auto">
                                                    <li class="nav-item">
                                                        <a class="nav-link{% if request.path == '/' %} active{% endif %}" href="/">Inicio</a>
                                                    </li>
                                                    <li class="nav-item">
                                                        <a class="nav-link{% if request.path == '/about' %} active{% endif %}" href="/about">Acerca
                                                            de</a>
                                                    </li>
                                                    <li class="nav-item">
                                                        <a class="nav-link{% if request.path == '/contact' %} active{% endif %}"
                                                            href="/contact">Contacto</a>
                                                    </li>
                                                    <li class="nav-item">
                                                        <a class="nav-link{% if request.path == '/order' %} active{% endif %}" href="/order">Pedido</a>
                                                    </li>
                                                    <!-- Agrega más enlaces según sea necesario -->
                                                </ul>
                                            </div>
                                        </div>
                                    </nav>

                                    <!-- Contenido Principal -->
                                    <div class="container mt-4">
                                        {% block content %}{% endblock %}
                                    </div>

                                    <!-- Footer -->
                                    <footer class="bg-light text-center py-4 mt-5">
                                        &copy; 2024 Pulztag. Todos los derechos reservados.
                                    </footer>

                                    <!-- Bootstrap JS y dependencias -->
                                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

                                    <!-- JS Personalizado -->
                                    <script src="{{ url_for('static', filename='js/script.js') }}"></script>

                                    {% block scripts %}{% endblock %}
                                </body>

                            </html>