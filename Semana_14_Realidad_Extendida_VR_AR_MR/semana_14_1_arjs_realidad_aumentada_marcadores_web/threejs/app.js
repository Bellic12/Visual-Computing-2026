/* ====================================================================
   app.js — Lógica de interacción de la experiencia AR.
   Responsabilidades:
     1. Escuchar los eventos markerFound / markerLost de cada <a-marker>.
     2. Actualizar el HUD (texto + color del punto de estado).
     3. Reproducir un sonido al detectar un marcador (bonus), con mute.
   ==================================================================== */

(function () {
  "use strict";

  // Estado global del sonido (el usuario puede silenciarlo desde el botón).
  let soundEnabled = true;

  // Mapa: id del marcador -> etiqueta legible que se muestra en el HUD.
  const MARKERS = {
    "marker-1": "Barcode 1 · Astronauta 3D",
    "marker-2": "Barcode 2 · Sistema solar",
    "marker-5": "Barcode 5 · Caja roja",
  };

  // Referencias a elementos del HUD.
  let statusText, statusDot, beep, muteBtn;

  document.addEventListener("DOMContentLoaded", init);

  function init() {
    statusText = document.getElementById("status-text");
    statusDot = document.getElementById("status-dot");
    beep = document.getElementById("beep");
    muteBtn = document.getElementById("mute-btn");

    // Botón de mute: alterna el flag y el icono.
    muteBtn.addEventListener("click", function () {
      soundEnabled = !soundEnabled;
      muteBtn.textContent = soundEnabled ? "🔊" : "🔇";
    });

    // Suscribir cada marcador a sus eventos de tracking.
    Object.keys(MARKERS).forEach(function (id) {
      const marker = document.getElementById(id);
      if (!marker) return;

      marker.addEventListener("markerFound", function () {
        onMarkerFound(MARKERS[id]);
      });

      marker.addEventListener("markerLost", function () {
        onMarkerLost();
      });
    });
  }

  /* Marcador detectado: actualizar HUD a verde y reproducir el beep. */
  function onMarkerFound(label) {
    setStatus(label, true);
    playBeep();
  }

  /* Marcador perdido: volver al estado de búsqueda. */
  function onMarkerLost() {
    setStatus("Buscando marcador…", false);
  }

  /* Actualiza el texto y el color del indicador de estado. */
  function setStatus(text, found) {
    statusText.textContent = text;
    statusDot.classList.toggle("found", found);
  }

  /* Reproduce el sonido de detección de forma segura.
     Si el archivo no existe o el navegador bloquea el autoplay,
     la app continúa sin interrumpirse. */
  function playBeep() {
    if (!soundEnabled || !beep) return;
    try {
      beep.currentTime = 0;
      const p = beep.play();
      if (p && typeof p.catch === "function") {
        p.catch(function () {/* autoplay bloqueado: se ignora */});
      }
    } catch (e) {
      /* sin sonido disponible: no es crítico */
    }
  }
})();
