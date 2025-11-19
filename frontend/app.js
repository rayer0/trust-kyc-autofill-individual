const API_BASE = "http://localhost:8000";

const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const extractedTextArea = document.getElementById("extracted-text");
const generateBtn = document.getElementById("generate-btn");
const resultsEl = document.getElementById("results");

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!fileInput.files.length) return;

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  resultsEl.innerHTML = "Processing document...";
  const response = await fetch(`${API_BASE}/api/process`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const message = await response.text();
    resultsEl.innerHTML = `<p class="error">${message}</p>`;
    return;
  }

  const data = await response.json();
  extractedTextArea.value = data.profile ? "" : data.text || "";
  renderResults(data);
});

generateBtn.addEventListener("click", async () => {
  const text = extractedTextArea.value.trim();
  if (!text) return;
  resultsEl.innerHTML = "Generating answers...";

  const response = await fetch(`${API_BASE}/api/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    const message = await response.text();
    resultsEl.innerHTML = `<p class="error">${message}</p>`;
    return;
  }

  const data = await response.json();
  renderResults(data);
});

function renderResults(data) {
  if (!data || !data.profile) {
    resultsEl.innerHTML = "No profile generated yet.";
    return;
  }

  const profileHtml = `
    <h2>Client Profile</h2>
    <pre>${JSON.stringify(data.profile, null, 2)}</pre>
  `;

  const formsHtml = data.forms
    .map(
      (form) => `
        <div class="form">
          <h3>${form.form_id} - ${form.form_title}</h3>
          <ul>
            ${form.answers
              .map(
                (answer) => `
                  <li>
                    <strong>${answer.question}:</strong> ${answer.answer || "—"}
                  </li>
                `
              )
              .join("")}
          </ul>
        </div>
      `
    )
    .join("");

  resultsEl.innerHTML = profileHtml + formsHtml;
}
