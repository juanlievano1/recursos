// Botones "Copiar": copian el texto del elemento que dice data-copia.
// Si el navegador no deja copiar, seleccionan el texto para copiarlo a mano.
document.querySelectorAll('[data-copia]').forEach(function (boton) {
  boton.addEventListener('click', function () {
    var fuente = document.getElementById(boton.dataset.copia);
    var texto = fuente.textContent.trim();
    var listo = function () {
      boton.textContent = 'Copiado';
      boton.classList.add('ok');
      setTimeout(function () { boton.textContent = 'Copiar'; boton.classList.remove('ok'); }, 1800);
    };
    var seleccionar = function () {
      var rango = document.createRange();
      rango.selectNodeContents(fuente);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(rango);
      boton.textContent = 'Ya está seleccionado';
      setTimeout(function () { boton.textContent = 'Copiar'; }, 2400);
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(texto).then(listo, seleccionar);
      } else {
        seleccionar();
      }
    } catch (e) {
      seleccionar();
    }
  });
});
