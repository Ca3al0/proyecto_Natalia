document.addEventListener('DOMContentLoaded', () => {
  // ---------- Alternar secciones Perfil / Direcciones / Pedidos ----------
  const menuPerfil = document.getElementById('menu-perfil');
  const menuDirecciones = document.getElementById('menu-direcciones');
  const menuPedidos = document.getElementById('menu-pedidos'); // Nuevo

  const seccionPerfil = document.getElementById('seccion-perfil');
  const seccionDirecciones = document.getElementById('seccion-direcciones');
  const seccionPedidos = document.getElementById('seccion-pedidos'); // Nuevo

  // Función para ocultar todas las secciones
  function ocultarSecciones() {
    seccionPerfil.style.display = 'none';
    seccionDirecciones.style.display = 'none';
    seccionPedidos.style.display = 'none';

    menuPerfil.classList.remove('active');
    menuDirecciones.classList.remove('active');
    menuPedidos.classList.remove('active');
  }

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

  // ---------- Modal de confirmación para borrar dirección ----------
  let urlBorrar = null;
  const modalBorrar = new bootstrap.Modal(document.getElementById('modalConfirmarBorrar'));

  document.querySelectorAll('.btn-borrar-direccion').forEach(btn => {
    btn.addEventListener('click', function () {
      urlBorrar = this.dataset.url;
      modalBorrar.show();
    });
  });

  // Formulario oculto para enviar POST al borrar
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
});
