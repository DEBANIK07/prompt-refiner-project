// AI Prompt Refiner - Frontend logic
// Talks to the FastAPI backend running at API_BASE.

const API_BASE = "http://localhost:8000";

const promptInput = document.getElementById("promptInput");
const refineBtn = document.getElementById("refineBtn");
const errorBox = document.getElementById("errorBox");
const loadingBox = document.getElementById("loadingBox");
const resultsSection = document.getElementById("resultsSection");

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function clearError() {
  errorBox.classList.add("hidden");
  errorBox.textContent = "";
}

function setLoading(isLoading) {
  loadingBox.classList.toggle("hidden", !isLoading);
  refineBtn.disabled = isLoading;
}

function renderResults(data) {
  resultsSection.innerHTML = "";
  resultsSection.classList.remove("hidden");

  data.variants.forEach((variant, index) => {
    const card = document.createElement("div");
    card.className = "variant-card";

    card.innerHTML = `
      <div class="variant-header">
        <span class="variant-label">Version ${index + 1}</span>
        <button class="copy-btn" data-index="${index}">Copy</button>
      </div>
      <div class="variant-text">${escapeHtml(variant.version)}</div>
      <div class="variant-explanation">${escapeHtml(variant.explanation)}</div>
    `;

    resultsSection.appendChild(card);
  });

  // Wire up copy buttons after render.
  resultsSection.querySelectorAll(".copy-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = Number(btn.dataset.index);
      navigator.clipboard.writeText(data.variants[idx].version);
      btn.textContent = "Copied!";
      setTimeout(() => (btn.textContent = "Copy"), 1500);
    });
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

async function refinePrompt() {
  const prompt = promptInput.value.trim();
  clearError();
  resultsSection.classList.add("hidden");

  if (!prompt) {
    showError("Please enter a prompt first.");
    return;
  }

  setLoading(true);

  try {
    const response = await fetch(`${API_BASE}/refine`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Request failed (${response.status})`);
    }

    const data = await response.json();
    renderResults(data);
  } catch (err) {
    showError(err.message || "Something went wrong. Is the backend running?");
  } finally {
    setLoading(false);
  }
}

refineBtn.addEventListener("click", refinePrompt);

promptInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
    refinePrompt();
  }
});
