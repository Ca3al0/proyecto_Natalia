  function seleccionarTodos() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name="ids"]');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    checkboxes.forEach(cb => cb.checked = !allChecked);
  }
