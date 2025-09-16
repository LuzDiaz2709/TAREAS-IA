// Año dinámico en el footer
document.getElementById("year").textContent = new Date().getFullYear();

// Menú responsive (solo visual; puedes expandirlo a dropdown si deseas)
const burger = document.querySelector(".burger");
const nav = document.querySelector(".nav nav");
if (burger) {
  burger.addEventListener("click", () => {
    nav.style.display = nav.style.display === "flex" ? "none" : "flex";
  });
}

// Animación de contadores para KPIs
function animateValue(el, target, duration = 1300) {
  const isFloat = String(target).includes(".");
  const end = parseFloat(target);
  const start = 0;
  const startTime = performance.now();

  function tick(now) {
    const p = Math.min((now - startTime) / duration, 1);
    const value = start + (end - start) * p;
    el.textContent = isFloat ? value.toFixed(1) : Math.floor(value);
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

// Reveal on scroll
const reveals = document.querySelectorAll(".reveal");
const io = new IntersectionObserver(
  entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add("in");
        const val = e.target.querySelector?.(".kpi__value");
        if (val && !val.dataset.done) {
          animateValue(val, val.dataset.target);
          val.dataset.done = "1";
        }
      }
    });
  },
  { threshold: 0.2 }
);
reveals.forEach(el => io.observe(el));

// CSS para la animación reveal (inyectado por JS para mantener el CSS limpio)
const style = document.createElement("style");
style.textContent = `
.reveal{opacity:0;transform:translateY(14px);transition:.6s ease}
.reveal.in{opacity:1;transform:none}
`;
document.head.appendChild(style);

// Chart.js — Línea de rendimiento (ejemplo)
const ctx = document.getElementById("lineChart");
if (ctx) {
  // Datos de ejemplo; luego los puedes reemplazar por tus métricas reales
  const data = {
    labels: ["Semana 1","Semana 2","Semana 3","Semana 4","Semana 5","Semana 6"],
    datasets: [
      {
        label: "Ingresos atribuidos",
        data: [1200, 1600, 1450, 2100, 2400, 2950],
        tension: 0.35,
        borderWidth: 3,
      },
      {
        label: "Inversión en Ads",
        data: [600, 700, 650, 800, 900, 950],
        tension: 0.35,
        borderWidth: 3,
      }
    ]
  };

  // Estilos adaptados al tema oscuro sin especificar colores fijos; Chart.js aplica por defecto
  const chart = new Chart(ctx, {
    type: "line",
    data,
    options: {
      responsive: true,
      plugins: {
        legend: { labels: { color: "#DDE3F1" } },
        tooltip: { mode: "index", intersect: false }
      },
      scales: {
        x: { ticks: { color: "#B9C0D4" }, grid: { color: "rgba(255,255,255,.06)" } },
        y: { ticks: { color: "#B9C0D4" }, grid: { color: "rgba(255,255,255,.06)" } }
      }
    }
  });
}

// Simulación de envío de formulario
const btn = document.getElementById("btnEnviar");
const msg = document.getElementById("formMsg");
if (btn && msg) {
  btn.addEventListener("click", () => {
    msg.textContent = "¡Gracias! Te contactaremos para agendar tu diagnóstico.";
    setTimeout(()=> msg.textContent = "", 5000);
  });
}
