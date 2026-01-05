async function submitPrediction() {
  const age = document.getElementById("age").value;
  const gender = document.getElementById("gender").value;
  const symptoms = document.getElementById("symptoms").value;

  const response = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ age, gender, symptoms })
  });

  const data = await response.json();

  localStorage.setItem("prediction", JSON.stringify(data));
  window.location.href = "/result";
}
async function submitContact(event) {
  event.preventDefault();

  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const message = document.getElementById("message").value;

  const response = await fetch("/api/contact", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, message })
  });

  if (response.ok) {
    document.getElementById("successBox").style.display = "block";
    event.target.reset();
  }
}
// Highlight active nav link
document.addEventListener("DOMContentLoaded", () => {
  const currentPath = window.location.pathname;
  document.querySelectorAll(".nav-menu a").forEach(link => {
    if (link.dataset.path === currentPath) {
      link.classList.add("active");
    }
  });
});

// Mobile menu toggle
function toggleMenu() {
  document.getElementById("navMenu").classList.toggle("show");
}
async function submitPrediction(event) {
  event.preventDefault();

  const age = document.querySelector("input[type='number']").value;
  const gender = document.querySelector("select").value;
  const symptoms = document.querySelector("textarea").value;

  const response = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ age, gender, symptoms })
  });

  const data = await response.json();

  // Store for result & explainability pages
  localStorage.setItem("prediction", JSON.stringify(data));

  // OPTIONAL: dummy explainability (for now)
  localStorage.setItem("explainability", JSON.stringify([
    { feature: "Fever", value: 0.42 },
    { feature: "Headache", value: 0.31 },
    { feature: "Fatigue", value: 0.18 },
    { feature: "Nausea", value: 0.09 }
  ]));

  // 🔥 THIS is what opens result.html
  window.location.href = "/result";
}
async function submitPrediction(event) {
  event.preventDefault();

  const age = document.querySelector("input[type='number']").value;
  const gender = document.querySelector("select").value;
  const symptoms = document.querySelector("textarea").value;

  const res = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ age, gender, symptoms })
  });

  const data = await res.json();

  localStorage.setItem("prediction", JSON.stringify(data));
  localStorage.setItem("explainability", JSON.stringify(data.features));
  localStorage.setItem("guidance", JSON.stringify({
    precautions: data.precautions,
    medicines: data.medicines
  }));

  window.location.href = "/result";
}

function renderProbabilityBars(predictions) {
  const container = document.getElementById("probabilityBars");
  container.innerHTML = "";

  predictions.forEach(item => {
    const row = document.createElement("div");
    row.className = "prob-row";

    row.innerHTML = `
      <div class="prob-label">
        <span>${item.disease}</span>
        <span>${item.confidence}%</span>
      </div>
      <div class="prob-bar">
        <div class="prob-fill" style="width:${item.confidence}%"></div>
      </div>
    `;

    container.appendChild(row);
  });
}
function renderProbabilityBars(predictions) {
  const container = document.getElementById("probabilityBars");
  container.innerHTML = "";

  predictions.forEach(item => {
    const row = document.createElement("div");
    row.className = "prob-row";

    row.innerHTML = `
      <div class="prob-label">
        <span>${item.disease}</span>
        <span>${item.confidence}%</span>
      </div>
      <div class="prob-bar">
        <div class="prob-fill" style="width:${item.confidence}%"></div>
      </div>
    `;

    container.appendChild(row);
  });
}
let allSymptoms = [];
let selectedSymptoms = new Set();

fetch("/api/symptoms")
  .then(res => res.json())
  .then(data => {
    allSymptoms = data;
  });

const input = document.getElementById("symptomInput");
const box = document.getElementById("suggestions");
const textarea = document.getElementById("symptoms");

input.addEventListener("input", () => {
  const value = input.value.toLowerCase();
  box.innerHTML = "";

  if (!value) {
    box.style.display = "none";
    return;
  }

  const matches = allSymptoms.filter(s =>
    s.toLowerCase().includes(value) &&
    !selectedSymptoms.has(s)
  ).slice(0, 8);

  if (matches.length === 0) {
    box.style.display = "none";
    return;
  }

  matches.forEach(symptom => {
    const div = document.createElement("div");
    div.className = "suggestion-item";
    div.textContent = symptom;

    div.onclick = () => {
      selectedSymptoms.add(symptom);
      textarea.value = Array.from(selectedSymptoms).join(", ");
      input.value = "";
      box.style.display = "none";
    };

    box.appendChild(div);
  });

  box.style.display = "block";
});
document.addEventListener("keydown", (e) => {
  // Ignore typing in inputs
  if (
    document.activeElement.tagName === "INPUT" ||
    document.activeElement.tagName === "TEXTAREA"
  ) return;

  // Left Arrow → Go Back
  if (e.key === "ArrowLeft") {
    window.history.back();
  }

  // Right Arrow → Forward (if possible)
  if (e.key === "ArrowRight") {
    window.history.forward();
  }
});
const symptomInput = document.getElementById("symptomInput");
const suggestionsBox = document.getElementById("suggestions");

let symptomHistory = JSON.parse(localStorage.getItem("symptomHistory")) || [];

// Fetch valid symptoms once
fetch("/api/symptoms")
  .then(res => res.json())
  .then(data => allSymptoms = data);

// Show suggestions
symptomInput.addEventListener("input", () => {
  const value = symptomInput.value.toLowerCase();
  suggestionsBox.innerHTML = "";

  if (!value) {
    suggestionsBox.style.display = "none";
    return;
  }

  const matches = [
    ...new Set([
      ...symptomHistory.filter(s => s.includes(value)),
      ...allSymptoms.filter(s => s.includes(value))
    ])
  ].slice(0, 8);

  matches.forEach(symptom => {
    const div = document.createElement("div");
    div.innerText = symptom;
    div.onclick = () => addSymptom(symptom);
    suggestionsBox.appendChild(div);
  });

  suggestionsBox.style.display = matches.length ? "block" : "none";
});

function addSymptom(symptom) {
  const textarea = document.getElementById("symptoms");
  if (!textarea.value.includes(symptom)) {
    textarea.value += (textarea.value ? ", " : "") + symptom;
  }
  suggestionsBox.style.display = "none";
  symptomInput.value = "";
}
