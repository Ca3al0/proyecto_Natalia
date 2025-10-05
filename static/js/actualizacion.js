document.addEventListener('DOMContentLoaded', () => {
  // ---------- Alternar secciones Perfil / Direcciones ----------
  const menuPerfil = document.getElementById('menu-perfil');
  const menuDirecciones = document.getElementById('menu-direcciones');

  const seccionPerfil = document.getElementById('seccion-perfil');
  const seccionDirecciones = document.getElementById('seccion-direcciones');

  menuPerfil.addEventListener('click', () => {
    seccionPerfil.style.display = 'block';
    seccionDirecciones.style.display = 'none';
    menuPerfil.classList.add('active');
    menuDirecciones.classList.remove('active');
  });

  menuDirecciones.addEventListener('click', () => {
    seccionPerfil.style.display = 'none';
    seccionDirecciones.style.display = 'block';
    menuDirecciones.classList.add('active');
    menuPerfil.classList.remove('active');
  });

  // ---------- Modal de confirmación para borrar dirección ----------
  let urlBorrar = null;
  const modalBorrar = new bootstrap.Modal(document.getElementById('modalConfirmarBorrar'));

  document.querySelectorAll('.btn-borrar-direccion').forEach(btn => {
    btn.addEventListener('click', function() {
      urlBorrar = this.dataset.url;
      modalBorrar.show();
    });
  });

  // Formulario oculto para enviar POST al borrar
  const formBorrar = document.createElement('form');
  formBorrar.method = 'POST';
  formBorrar.style.display = 'none';
  document.body.appendChild(formBorrar);

  document.getElementById('btnConfirmarBorrar').addEventListener('click', function() {
    if(urlBorrar){
      formBorrar.action = urlBorrar;
      formBorrar.submit();
    }
  });
});
