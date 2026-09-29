/**
 * EduGenie Frontend Controller
 * Connects UI interactions to FastAPI backend endpoints.
 */

// Global State
let currentQuizData = null;

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  checkSystemHealth();
});

// ==========================================
// Tab Navigation
// ==========================================
function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(content => {
        content.classList.remove("active");
      });

      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
      }
      hideError();
    });
  });
}

// ==========================================
// System Health Check
// ==========================================
async function checkSystemHealth() {
  const statusEl = document.getElementById("system-status");
  try {
    const res = await fetch("/health");
    if (res.ok) {
      statusEl.querySelector(".status-dot").style.backgroundColor = "var(--success)";
      statusEl.querySelector(".status-text").textContent = "Online";
    } else {
      statusEl.querySelector(".status-dot").style.backgroundColor = "var(--warning)";
      statusEl.querySelector(".status-text").textContent = "Degraded";
    }
  } catch (err) {
    statusEl.querySelector(".status-dot").style.backgroundColor = "var(--danger)";
    statusEl.querySelector(".status-text").textContent = "Offline";
  }
}

// ==========================================
// UI Helper Functions
// ==========================================
function setLoading(buttonId, isLoading, loadingText = "EduGenie is thinking...") {
  const btn = document.getElementById(buttonId);
  if (!btn) return;
  const spinner = btn.querySelector(".btn-spinner");
  const textSpan = btn.querySelector(".btn-text");

  if (isLoading) {
    btn.disabled = true;
    if (spinner) spinner.style.display = "inline-block";
    if (textSpan) {
      btn.dataset.originalText = textSpan.textContent;
      textSpan.textContent = loadingText;
    }
  } else {
    btn.disabled = false;
    if (spinner) spinner.style.display = "none";
    if (textSpan && btn.dataset.originalText) {
      textSpan.textContent = btn.dataset.originalText;
    }
  }
}

function showError(message) {
  const errorBanner = document.getElementById("global-error");
  const errorText = document.getElementById("global-error-text");
  errorText.innerHTML = message;
  errorBanner.style.display = "flex";
  errorBanner.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function hideError() {
  const errorBanner = document.getElementById("global-error");
  if (errorBanner) {
    errorBanner.style.display = "none";
  }
}

function closeGlobalError() {
  hideError();
}

function renderMarkdown(targetElementId, markdownText) {
  const el = document.getElementById(targetElementId);
  if (!el) return;
  if (typeof marked !== "undefined" && marked.parse) {
    el.innerHTML = marked.parse(markdownText);
  } else {
    // Fallback if marked is not loaded
    el.textContent = markdownText;
  }
}

function copyResult(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const text = el.innerText || el.textContent;
  navigator.clipboard.writeText(text).then(() => {
    alert("Copied to clipboard!");
  }).catch(() => {
    alert("Could not copy text.");
  });
}

// ==========================================
// 1. Q&A Handler
// ==========================================
function setQaInput(text) {
  const input = document.getElementById("qa-input");
  input.value = text;
  input.focus();
}

async function handleQaSubmit() {
  hideError();
  const input = document.getElementById("qa-input");
  const question = input.value.trim();

  if (!question) {
    showError("Please enter a question to ask EduGenie.");
    input.focus();
    return;
  }

  setLoading("qa-submit", true, "Searching knowledge base...");
  const resultCard = document.getElementById("qa-result");

  try {
    const res = await fetch(`/qa?question=${encodeURIComponent(question)}`);
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || data.error || "Failed to get an answer.");
    }

    renderMarkdown("qa-output", data.answer);
    resultCard.style.display = "block";
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (err) {
    showError(`<strong>Q&A Error:</strong> ${err.message}`);
  } finally {
    setLoading("qa-submit", false);
  }
}

// ==========================================
// 2. Explanation Handler
// ==========================================
function setExplainInput(text) {
  const input = document.getElementById("explain-input");
  input.value = text;
  input.focus();
}

async function handleExplainSubmit() {
  hideError();
  const input = document.getElementById("explain-input");
  const topic = input.value.trim();

  if (!topic) {
    showError("Please enter a topic or concept to explain.");
    input.focus();
    return;
  }

  setLoading("explain-submit", true, "Explaining concept (LaMini-Flan-T5)...");
  const resultCard = document.getElementById("explain-result");

  try {
    const res = await fetch("/explain/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic: topic })
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || data.error || "Failed to generate explanation.");
    }

    document.getElementById("explain-topic-title").textContent = `Explanation: ${data.topic || topic}`;
    renderMarkdown("explain-output", data.explanation);
    resultCard.style.display = "block";
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (err) {
    showError(`<strong>Explanation Error:</strong> ${err.message}`);
  } finally {
    setLoading("explain-submit", false);
  }
}

// ==========================================
// 3. Summarization Handler
// ==========================================
function loadSampleSummary() {
  const sample = `Photosynthesis is the biological process by which green plants, algae, and certain bacteria convert light energy into chemical energy. During this biochemical reaction, plants absorb sunlight via chlorophyll pigments within chloroplasts. They take in carbon dioxide from the ambient atmosphere through microscopic stomata and draw water from the soil through their root systems. Using photon energy, water molecules are split into hydrogen ions and oxygen gas in light-dependent reactions. The oxygen is expelled into the biosphere as a crucial byproduct. Subsequently, during the Calvin cycle (light-independent reactions), the plant fixes carbon dioxide to synthesize glucose and other simple carbohydrates, which serve as foundational cellular fuel across all terrestrial ecosystems.`;
  const input = document.getElementById("summary-input");
  input.value = sample;
  input.focus();
}

async function handleSummarySubmit() {
  hideError();
  const input = document.getElementById("summary-input");
  const text = input.value.trim();

  if (!text) {
    showError("Please enter or paste an educational passage to summarize.");
    input.focus();
    return;
  }

  setLoading("summary-submit", true, "Summarizing text...");
  const resultCard = document.getElementById("summary-result");

  try {
    const res = await fetch("/summarize/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || data.error || "Failed to summarize text.");
    }

    renderMarkdown("summary-output", data.summary);
    resultCard.style.display = "block";
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (err) {
    showError(`<strong>Summarization Error:</strong> ${err.message}`);
  } finally {
    setLoading("summary-submit", false);
  }
}

// ==========================================
// 4. Interactive Quiz Handler
// ==========================================
function setQuizInput(text) {
  const input = document.getElementById("quiz-input");
  input.value = text;
  input.focus();
}

async function handleQuizSubmit() {
  hideError();
  const input = document.getElementById("quiz-input");
  const topic = input.value.trim();

  if (!topic) {
    showError("Please enter a topic or passage for the quiz.");
    input.focus();
    return;
  }

  setLoading("quiz-submit", true, "Generating 3-question quiz...");
  const quizContainer = document.getElementById("quiz-container");

  try {
    const res = await fetch("/quiz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic: topic })
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || data.error || "Failed to generate quiz.");
    }

    if (!data.quiz || !Array.isArray(data.quiz) || data.quiz.length === 0) {
      throw new Error("Invalid quiz structure returned by server.");
    }

    currentQuizData = data.quiz;
    renderQuizUI(topic, currentQuizData);
    quizContainer.style.display = "block";
    quizContainer.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (err) {
    showError(`<strong>Quiz Generation Error:</strong> ${err.message}`);
  } finally {
    setLoading("quiz-submit", false);
  }
}

function renderQuizUI(topic, questions) {
  document.getElementById("quiz-title").textContent = `Quiz: ${topic}`;
  const scoreBadge = document.getElementById("quiz-score-badge");
  scoreBadge.style.display = "none";
  scoreBadge.className = "score-badge";

  document.getElementById("quiz-check-btn").style.display = "inline-flex";
  document.getElementById("quiz-retry-btn").style.display = "none";

  const listEl = document.getElementById("quiz-questions-list");
  listEl.innerHTML = "";

  questions.forEach((q, qIndex) => {
    const card = document.createElement("div");
    card.className = "quiz-q-card";
    card.id = `quiz-card-${qIndex}`;

    // Question header
    const title = document.createElement("div");
    title.className = "quiz-q-title";
    title.innerHTML = `<span class="quiz-q-num">Q${qIndex + 1}.</span> <span>${escapeHtml(q.question)}</span>`;
    card.appendChild(title);

    // Options container
    const optionsDiv = document.createElement("div");
    optionsDiv.className = "quiz-options-list";

    q.options.forEach((opt, optIndex) => {
      const optLabel = document.createElement("label");
      optLabel.className = "quiz-option";
      optLabel.id = `opt-${qIndex}-${optIndex}`;

      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = `quiz-question-${qIndex}`;
      radio.value = opt;

      const optSpan = document.createElement("span");
      optSpan.className = "quiz-option-text";
      optSpan.textContent = opt;

      optLabel.appendChild(radio);
      optLabel.appendChild(optSpan);
      optionsDiv.appendChild(optLabel);
    });

    card.appendChild(optionsDiv);

    // Feedback message box for this question
    const feedbackBox = document.createElement("div");
    feedbackBox.className = "quiz-explanation-box";
    feedbackBox.id = `quiz-feedback-${qIndex}`;
    card.appendChild(feedbackBox);

    listEl.appendChild(card);
  });
}

function checkQuizAnswers() {
  if (!currentQuizData) return;

  hideError();

  // Validate that student answered all questions
  let allAnswered = true;
  for (let i = 0; i < currentQuizData.length; i++) {
    const selected = document.querySelector(`input[name="quiz-question-${i}"]:checked`);
    if (!selected) {
      allAnswered = false;
      break;
    }
  }

  if (!allAnswered) {
    showError("Please answer all questions before submitting the quiz.");
    return;
  }

  let correctCount = 0;

  currentQuizData.forEach((q, qIndex) => {
    const selectedRadio = document.querySelector(`input[name="quiz-question-${qIndex}"]:checked`);
    const userSelectedVal = selectedRadio ? selectedRadio.value.trim() : null;
    const correctVal = q.answer.trim();
    const feedbackBox = document.getElementById(`quiz-feedback-${qIndex}`);

    // Disable all radio buttons for this question
    document.querySelectorAll(`input[name="quiz-question-${qIndex}"]`).forEach(r => r.disabled = true);

    // Highlight options
    q.options.forEach((opt, optIndex) => {
      const optLabel = document.getElementById(`opt-${qIndex}-${optIndex}`);
      optLabel.classList.remove("correct-choice", "wrong-choice");

      const optTrimmed = opt.trim();
      if (optTrimmed === correctVal) {
        optLabel.classList.add("correct-choice");
      } else if (userSelectedVal === optTrimmed && optTrimmed !== correctVal) {
        optLabel.classList.add("wrong-choice");
      }
    });

    if (userSelectedVal === correctVal) {
      correctCount++;
      feedbackBox.className = "quiz-explanation-box correct";
      feedbackBox.innerHTML = `<strong>Correct!</strong> Well done.`;
    } else {
      feedbackBox.className = "quiz-explanation-box incorrect";
      feedbackBox.innerHTML = `<strong>Incorrect.</strong> The correct answer is: <u>${escapeHtml(correctVal)}</u>`;
    }
  });

  // Calculate and display overall score
  const total = currentQuizData.length;
  const percentage = Math.round((correctCount / total) * 100);
  const scoreBadge = document.getElementById("quiz-score-badge");
  scoreBadge.textContent = `Score: ${correctCount} / ${total} (${percentage}%)`;
  scoreBadge.style.display = "inline-block";
  if (correctCount === total) {
    scoreBadge.classList.add("perfect");
  }

  document.getElementById("quiz-check-btn").style.display = "none";
  document.getElementById("quiz-retry-btn").style.display = "inline-flex";
}

function resetQuizSelections() {
  if (!currentQuizData) return;
  hideError();

  currentQuizData.forEach((q, qIndex) => {
    document.querySelectorAll(`input[name="quiz-question-${qIndex}"]`).forEach(r => {
      r.disabled = false;
      r.checked = false;
    });

    q.options.forEach((opt, optIndex) => {
      const optLabel = document.getElementById(`opt-${qIndex}-${optIndex}`);
      if (optLabel) optLabel.classList.remove("correct-choice", "wrong-choice");
    });

    const feedbackBox = document.getElementById(`quiz-feedback-${qIndex}`);
    if (feedbackBox) {
      feedbackBox.className = "quiz-explanation-box";
      feedbackBox.style.display = "none";
      feedbackBox.innerHTML = "";
    }
  });

  const scoreBadge = document.getElementById("quiz-score-badge");
  scoreBadge.style.display = "none";
  scoreBadge.className = "score-badge";

  document.getElementById("quiz-check-btn").style.display = "inline-flex";
  document.getElementById("quiz-retry-btn").style.display = "none";
}

// ==========================================
// 5. Learning Recommendations Handler
// ==========================================
function setLearningInput(text) {
  const input = document.getElementById("learning-input");
  input.value = text;
  input.focus();
}

async function handleLearningSubmit() {
  hideError();
  const input = document.getElementById("learning-input");
  const topic = input.value.trim();

  if (!topic) {
    showError("Please enter a subject or skill to generate learning recommendations.");
    input.focus();
    return;
  }

  setLoading("learning-submit", true, "Designing structured roadmap...");
  const resultCard = document.getElementById("learning-result");

  try {
    const res = await fetch(`/learning-recommendations?topic=${encodeURIComponent(topic)}`);
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || data.error || "Failed to generate learning recommendations.");
    }

    document.getElementById("learning-title").textContent = `Learning Roadmap: ${data.topic || topic}`;
    renderMarkdown("learning-output", data.recommendation);
    resultCard.style.display = "block";
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (err) {
    showError(`<strong>Learning Path Error:</strong> ${err.message}`);
  } finally {
    setLoading("learning-submit", false);
  }
}

// Security helper
function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
