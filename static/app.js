const form = document.querySelector("#chat-form");
const input = document.querySelector("#question");
const sendButton = document.querySelector("#send-button");
const conversation = document.querySelector("#conversation");
const welcome = document.querySelector("#welcome");

function addMessage(text, role) {
  const element = document.createElement("div");
  element.className = `message ${role}`;
  element.textContent = text;
  conversation.append(element);
  element.scrollIntoView({ behavior: "smooth", block: "end" });
  return element;
}

function addAnswer(data) {
  const wrapper = document.createElement("article");
  wrapper.className = "message assistant";

  const answer = document.createElement("div");
  answer.className = "answer-text";
  answer.textContent = data.answer;
  wrapper.append(answer);

  const meta = document.createElement("div");
  meta.className = "answer-meta";
  meta.textContent = data.sources?.length
    ? `Source support: ${Math.round(data.confidence_score)}/100`
    : "No supporting source found in the demo knowledge base";
  wrapper.append(meta);

  if (Array.isArray(data.sources) && data.sources.length) {
    const details = document.createElement("details");
    details.className = "sources";
    const summary = document.createElement("summary");
    summary.textContent = `Sources (${data.sources.length})`;
    details.append(summary);

    for (const source of data.sources) {
      const item = document.createElement("div");
      item.className = "source-item";
      const title = document.createElement("div");
      title.textContent = source.section_title || source.chunk_id;
      const sub = document.createElement("div");
      sub.textContent = [
        source.subsection,
        source.source_pages?.length ? `Page(s): ${source.source_pages.join(", ")}` : "",
      ].filter(Boolean).join(" · ");
      item.append(title, sub);
      details.append(item);
    }
    wrapper.append(details);
  }

  conversation.append(wrapper);
  wrapper.scrollIntoView({ behavior: "smooth", block: "end" });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = input.value.trim();
  if (!query || sendButton.disabled) return;

  welcome?.remove();
  addMessage(query, "user");
  input.value = "";
  input.style.height = "auto";
  sendButton.disabled = true;
  input.disabled = true;

  const pending = addMessage("Thinking…", "assistant");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || payload.error?.message || `Request failed (${response.status})`);
    }
    pending.remove();
    addAnswer(payload);
  } catch (error) {
    pending.remove();
    addMessage(error.message || "The request could not be completed. Please try again.", "assistant error");
  } finally {
    sendButton.disabled = false;
    input.disabled = false;
    input.focus();
  }
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
