const messages = document.getElementById("messages");
const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const newChat = document.getElementById("newChat");

function getSessionId() {
  let id = localStorage.getItem("ee_bot_session");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("ee_bot_session", id);
  }
  return id;
}

function addMessage(role, text, sources = []) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  if (sources.length) {
    const src = document.createElement("div");
    src.className = "sources";
    const names = [...new Set(sources.map(s => s.display_name || s.filename))];
    src.textContent = `المصادر: ${names.join("، ")}`;
    bubble.appendChild(src);
  }

  article.appendChild(bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  addMessage("user", text);
  input.value = "";
  sendButton.disabled = true;

  const typing = document.createElement("article");
  typing.className = "message bot";
  typing.innerHTML = '<div class="bubble">بدور بالتعليمات والملفات...</div>';
  messages.appendChild(typing);
  messages.scrollTop = messages.scrollHeight;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        session_id: getSessionId(),
        message: text
      })
    });

    const data = await res.json();
    typing.remove();

    if (!res.ok) {
      addMessage("bot", data.detail || "صار خطأ غير متوقع.");
      return;
    }

    addMessage("bot", data.answer, data.sources || []);
  } catch (err) {
    typing.remove();
    addMessage("bot", "تعذر الاتصال بالخادم. تأكد إن السيرفر شغال.");
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
});

newChat.addEventListener("click", async () => {
  const oldId = getSessionId();
  try { await fetch(`/api/chat/${oldId}`, {method: "DELETE"}); } catch (_) {}
  localStorage.removeItem("ee_bot_session");
  location.reload();
});
