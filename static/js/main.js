// Cerrar flashes automáticamente después de 3 segundos
setTimeout(() => {
  document.querySelectorAll('.flash-small, .alert').forEach(alert => {
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(100%)';
    alert.style.transition = 'all 0.5s ease';
    setTimeout(() => alert.remove(), 500);
  });
}, 3000);
