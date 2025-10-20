document.addEventListener('DOMContentLoaded', () => {
  // Referencias a los menús y secciones
  const menuPerfil = document.getElementById('menu-perfil');
  const menuDirecciones = document.getElementById('menu-direcciones');
  const menuPedidos = document.getElementById('menu-pedidos');

  const seccionPerfil = document.getElementById('seccion-perfil');
  const seccionDirecciones = document.getElementById('seccion-direcciones');
  const seccionPedidos = document.getElementById('seccion-pedidos');

  // Función para ocultar secciones
  function ocultarSecciones() {
    seccionPerfil.style.display = 'none';
    seccionDirecciones.style.display = 'none';
    seccionPedidos.style.display = 'none';

    menuPerfil.classList.remove('active');
    menuDirecciones.classList.remove('active');
    menuPedidos.classList.remove('active');
  }

  // Mostrar cada sección al hacer clic
  menuPerfil.addEventListener('click', () => {
    ocultarSecciones();
    seccionPerfil.style.display = 'block';
    menuPerfil.classList.add('active');
  });

  menuDirecciones.addEventListener('click', () => {
    ocultarSecciones();
    seccionDirecciones.style.display = 'block';
    menuDirecciones.classList.add('active');
  });

  menuPedidos.addEventListener('click', () => {
    ocultarSecciones();
    seccionPedidos.style.display = 'block';
    menuPedidos.classList.add('active');
  });

  // --- BORRAR DIRECCIÓN ---
  let urlBorrar = null;
  const modalBorrar = new bootstrap.Modal(document.getElementById('modalConfirmarBorrar'));

  document.querySelectorAll('.btn-borrar-direccion').forEach(btn => {
    btn.addEventListener('click', function () {
      urlBorrar = this.dataset.url;
      modalBorrar.show();
    });
  });

  const formBorrar = document.createElement('form');
  formBorrar.method = 'POST';
  formBorrar.style.display = 'none';
  document.body.appendChild(formBorrar);

  document.getElementById('btnConfirmarBorrar').addEventListener('click', function () {
    if (urlBorrar) {
      formBorrar.action = urlBorrar;
      formBorrar.submit();
    }
  });

// --- VER DETALLES DE PEDIDO ---
const modalPedido = document.getElementById('modalPedido');

modalPedido.addEventListener('show.bs.modal', event => {
  const button = event.relatedTarget;
  const pedidoId = button.getAttribute('data-id');
  const contenido = document.getElementById('detalle-pedido-contenido');

  // Muestra mensaje mientras carga
  contenido.innerHTML = `<p class="text-muted">Cargando detalles del pedido #${pedidoId}...</p>`;

  // 🔗 Petición al servidor para obtener el detalle del pedido
  fetch(`/cliente/pedido/${pedidoId}/detalle`)
    .then(response => {
      if (!response.ok) throw new Error('Error al obtener los detalles del pedido.');
      return response.text();
    })
    .then(html => {
      contenido.innerHTML = html; // Inserta el HTML del detalle del pedido
    })
    .catch(error => {
      contenido.innerHTML = `<p class="text-danger">❌ No se pudieron cargar los detalles: ${error.message}</p>`;
    });
});
});
