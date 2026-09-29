# app.py
# ============================================================
# AI GAME STUDIO — MULTI-AGENT STREAMLIT ORCHESTRATOR
# ============================================================
#
# Архитектура:
#
# Gemini 3.5  -> Архитектор / создание ядра / Project Map
# Gemini 3.7  -> Gameplay / механики
# Qwen        -> AI ботов / логика
# Kimi        -> Visual / UI / polish
# DeepSeek    -> QA / реальный игрок / bug reports
# Gemini 3.8  -> Boss / final review / final JSON
#
# Все запросы идут через OpenRouter + OpenAI SDK.
#
# CRITICAL:
# - API errors не должны ронять Streamlit
# - JSON можно извлекать даже если модель обернула его в ```json
# - повреждённый ответ агента не уничтожает проект
# - DeepSeek loop максимум 3 итерации
# - ZIP создаётся в памяти
# - preview собирается из HTML/CSS/JS
# ============================================================

import os
import io
import re
import json
import time
import html
import zipfile
import traceback
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Game Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CYBERPUNK UI
# ============================================================

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Orbitron:wght@500;700;900&display=swap');

    .stApp {
        background:
            radial-gradient(circle at 20% 10%, rgba(0,255,200,.07), transparent 25%),
            radial-gradient(circle at 80% 20%, rgba(150,0,255,.08), transparent 25%),
            #05070b;
        color: #e8faff;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 1px;
    }

    .cyber-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 42px;
        font-weight: 900;
        color: #00ffd5;
        text-shadow:
            0 0 5px rgba(0,255,213,.7),
            0 0 20px rgba(0,255,213,.35);
        margin-bottom: 5px;
    }

    .cyber-subtitle {
        color: #8997aa;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 25px;
    }

    .terminal {
        background: #020407;
        border: 1px solid #16333a;
        border-radius: 10px;
        padding: 15px;
        font-family: 'JetBrains Mono', monospace;
        min-height: 250px;
        max-height: 550px;
        overflow-y: auto;
        box-shadow:
            inset 0 0 30px rgba(0,255,200,.025),
            0 0 20px rgba(0,255,200,.03);
    }

    .terminal-line {
        margin: 3px 0;
        line-height: 1.45;
        font-size: 13px;
    }

    .terminal-time {
        color: #51616e;
    }

    .terminal-agent {
        color: #b65cff;
        font-weight: bold;
    }

    .terminal-ok {
        color: #00ff9d;
    }

    .terminal-warn {
        color: #ffd166;
    }

    .terminal-error {
        color: #ff5577;
    }

    .terminal-info {
        color: #5edbff;
    }

    .agent-card {
        background: rgba(10,15,23,.85);
        border: 1px solid #18333b;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }

    .agent-name {
        font-family: 'Orbitron', sans-serif;
        color: #00ffd5;
        font-size: 16px;
        font-weight: bold;
    }

    .agent-role {
        color: #81909e;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        margin-top: 4px;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #00a98f, #00d9bb);
        color: #00110d;
        border: none;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        border-radius: 7px;
        padding: 0.65rem 1.2rem;
        box-shadow: 0 0 15px rgba(0,255,213,.15);
    }

    div.stButton > button:hover {
        box-shadow: 0 0 25px rgba(0,255,213,.35);
        transform: translateY(-1px);
    }

    textarea, input {
        background-color: #080c12 !important;
        color: #e8faff !important;
        border-color: #19353d !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .status-ok {
        padding: 10px;
        border-left: 3px solid #00ff9d;
        background: rgba(0,255,157,.04);
    }

    .status-error {
        padding: 10px;
        border-left: 3px solid #ff5577;
        background: rgba(255,85,119,.04);
    }

    .status-warning {
        padding: 10px;
        border-left: 3px solid #ffd166;
        background: rgba(255,209,102,.04);
    }

    .small-muted {
        color: #667789;
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;
    }

    code {
        color: #00ffd5 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# CONSTANTS
# ============================================================

MAX_QA_ITERATIONS = 3
MAX_RETRIES_PER_CALL = 2
API_TIMEOUT = 120

MAX_FILE_SIZE = 250_000
MAX_TOTAL_PROJECT_CHARS = 150_000
MAX_PROMPT_CHARS = 180_000

ALLOWED_TEXT_EXTENSIONS = {
    ".html",
    ".htm",
    ".css",
    ".js",
    ".mjs",
    ".json",
    ".txt",
    ".md",
    ".svg",
    ".xml",
    ".glsl",
    ".vert",
    ".frag",
    ".ts",
}

# ============================================================
# AGENT MODEL CONFIG
# ============================================================
#
# ВАЖНО:
# "Gemini 3.5" и т.д. — именно названия ролей.
# Реальные OpenRouter slug'и задаются через ENV.
#
# Например в Render:
#
# GEMINI_35_MODEL=google/...
# GEMINI_37_MODEL=google/...
# QWEN_MODEL=qwen/...
# KIMI_MODEL=moonshotai/...
# DEEPSEEK_MODEL=deepseek/...
# GEMINI_38_MODEL=google/...
#
# Если переменная не задана, используется literal slug.
# Если slug не существует — safe_api_call поймает ошибку.
# ============================================================

AGENTS = {
    "gemini_35": {
        "name": "Gemini 3.5",
        "role": "ARCHITECT / CORE",
        "model": os.getenv("GEMINI_35_MODEL", "gemini-3.5"),
    },
    "gemini_37": {
        "name": "Gemini 3.7",
        "role": "GAMEPLAY ENGINEER",
        "model": os.getenv("GEMINI_37_MODEL", "gemini-3.7"),
    },
    "qwen": {
        "name": "Qwen",
        "role": "BOT AI / LOGIC",
        "model": os.getenv("QWEN_MODEL", "qwen"),
    },
    "kimi": {
        "name": "Kimi",
        "role": "VISUAL / UI / POLISH",
        "model": os.getenv("KIMI_MODEL", "kimi"),
    },
    "deepseek": {
        "name": "DeepSeek",
        "role": "QA / PLAYER TESTER",
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek"),
    },
    "gemini_38": {
        "name": "Gemini 3.8",
        "role": "BOSS / FINAL REVIEW",
        "model": os.getenv("GEMINI_38_MODEL", "gemini-3.8"),
    },
}


# ============================================================
# SESSION STATE
# ============================================================

if "logs" not in st.session_state:
    st.session_state.logs = []

if "project_files" not in st.session_state:
    st.session_state.project_files = {}

if "project_map" not in st.session_state:
    st.session_state.project_map = {}

if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

if "final_zip" not in st.session_state:
    st.session_state.final_zip = None

if "final_project" not in st.session_state:
    st.session_state.final_project = {}

if "generation_finished" not in st.session_state:
    st.session_state.generation_finished = False


# ============================================================
# LOGGING
# ============================================================

def log(message: str, level: str = "info", agent: Optional[str] = None):
    """
    Безопасный внутренний лог.
    Никогда не должен бросать исключение.
    """
    try:
        timestamp = time.strftime("%H:%M:%S")

        prefix = ""
        if agent:
            prefix = f"[{agent}] "

        st.session_state.logs.append(
            {
                "time": timestamp,
                "level": level,
                "message": prefix + str(message),
            }
        )

        # Ограничиваем память UI.
        if len(st.session_state.logs) > 500:
            st.session_state.logs = st.session_state.logs[-500:]

    except Exception:
        # Логирование никогда не должно ломать приложение.
        pass


def render_terminal():
    try:
        lines = []

        for item in st.session_state.logs[-250:]:
            level = item.get("level", "info")
            css_class = f"terminal-{level}"

            lines.append(
                f"""
                <div class="terminal-line">
                    <span class="terminal-time">
                        [{html.escape(str(item.get("time", "")))}]
                    </span>
                    <span class="{css_class}">
                        {html.escape(str(item.get("message", "")))}
                    </span>
                </div>
                """
            )

        if not lines:
            lines.append(
                '<div class="terminal-line terminal-info">'
                "SYSTEM READY..."
                "</div>"
            )

        st.markdown(
            '<div class="terminal">' + "".join(lines) + "</div>",
            unsafe_allow_html=True,
        )

    except Exception:
        st.warning("Не удалось отрисовать системный терминал.")


# ============================================================
# SAFE STRING HELPERS
# ============================================================

def clean_text(value: Any, default: str = "") -> str:
    try:
        if value is None:
            return default
        return str(value)
    except Exception:
        return default


def trim_text(value: str, limit: int) -> str:
    value = clean_text(value)

    if len(value) <= limit:
        return value

    return (
        value[:limit]
        + "\n\n/* [TRUNCATED BY ORCHESTRATOR] */\n"
    )


# ============================================================
# SAFE JSON PARSER
# ============================================================

def extract_json(raw: Any) -> Optional[Any]:
    """
    Пытается достать JSON из:
    1. обычного JSON
    2. ```json ... ```
    3. ``` ... ```
    4. текста до/после JSON
    5. balanced {...} / [...]
    """

    try:
        if raw is None:
            return None

        text = clean_text(raw).strip()

        if not text:
            return None

        # 1. Direct JSON.
        try:
            return json.loads(text)
        except Exception:
            pass

        # 2. Markdown JSON block.
        fenced = re.findall(
            r"```(?:json|JSON)?\s*(.*?)```",
            text,
            flags=re.DOTALL,
        )

        for block in fenced:
            try:
                return json.loads(block.strip())
            except Exception:
                continue

        # 3. Search balanced JSON objects.
        starts = []

        for i, char in enumerate(text):
            if char in "{[":
                starts.append(i)

        for start in starts:
            opening = text[start]
            closing = "}" if opening == "{" else "]"

            depth = 0
            in_string = False
            escape = False

            for i in range(start, len(text)):
                char = text[i]

                if escape:
                    escape = False
                    continue

                if char == "\\" and in_string:
                    escape = True
                    continue

                if char == '"':
                    in_string = not in_string
                    continue

                if in_string:
                    continue

                if char == opening:
                    depth += 1

                elif char == closing:
                    depth -= 1

                    if depth == 0:
                        candidate = text[start : i + 1]

                        try:
                            return json.loads(candidate)
                        except Exception:
                            break

    except Exception:
        return None

    return None


# ============================================================
# PROJECT FILE SAFETY
# ============================================================

def sanitize_path(path: Any) -> Optional[str]:
    """
    Защищает ZIP от:
    ../
    абсолютных путей
    Windows traversal
    пустых имён
    """

    try:
        path = clean_text(path).strip()
        path = path.replace("\\", "/")

        if not path:
            return None

        # Запрещаем absolute Unix path.
        if path.startswith("/"):
            return None

        # Windows drive.
        if re.match(r"^[A-Za-z]:", path):
            return None

        parts = []

        for part in path.split("/"):
            part = part.strip()

            if not part or part == ".":
                continue

            if part == "..":
                return None

            # Не даём писать в скрытые системные места.
            if part in {"__pycache__", ".git"}:
                return None

            parts.append(part)

        if not parts:
            return None

        clean = "/".join(parts)

        if len(clean) > 240:
            return None

        return clean

    except Exception:
        return None


def normalize_files(raw_files: Any) -> Dict[str, str]:
    """
    Принимает:
      {"index.html": "..."}
    или:
      [{"path": "index.html", "content": "..."}]
    """

    result: Dict[str, str] = {}

    try:
        if isinstance(raw_files, dict):
            iterator = [
                {"path": k, "content": v}
                for k, v in raw_files.items()
            ]

        elif isinstance(raw_files, list):
            iterator = raw_files

        else:
            return {}

        for item in iterator:
            try:
                if not isinstance(item, dict):
                    continue

                path = sanitize_path(
                    item.get("path")
                    or item.get("name")
                    or item.get("file")
                )

                if not path:
                    continue

                content = item.get("content", "")

                if content is None:
                    content = ""

                if not isinstance(content, str):
                    content = json.dumps(
                        content,
                        ensure_ascii=False,
                        indent=2,
                    )

                if len(content) > MAX_FILE_SIZE:
                    content = trim_text(
                        content,
                        MAX_FILE_SIZE,
                    )

                result[path] = content

            except Exception:
                continue

    except Exception:
        return {}

    return result


# ============================================================
# PROJECT MAP
# ============================================================

def build_project_map(files: Dict[str, str]) -> Dict[str, Any]:
    """
    Автоматически строит карту проекта.
    """

    result = {
        "files": [],
        "directories": [],
    }

    directories = set()

    try:
        for path in sorted(files.keys()):
            result["files"].append(path)

            parts = path.split("/")[:-1]

            for i in range(1, len(parts) + 1):
                directories.add("/".join(parts[:i]))

        result["directories"] = sorted(directories)

    except Exception:
        pass

    return result


def project_to_text(
    files: Dict[str, str],
    max_chars: int = MAX_TOTAL_PROJECT_CHARS,
) -> str:
    """
    Сериализует проект для контекста агента.
    """

    try:
        chunks = []
        total = 0

        for path in sorted(files.keys()):
            content = files[path]

            block = (
                f"\n===== FILE: {path} =====\n"
                f"{content}\n"
                f"===== END FILE: {path} =====\n"
            )

            if total + len(block) > max_chars:
                remaining = max_chars - total

                if remaining > 300:
                    chunks.append(block[:remaining])

                chunks.append(
                    "\n===== PROJECT CONTEXT TRUNCATED =====\n"
                )

                break

            chunks.append(block)
            total += len(block)

        return "".join(chunks)

    except Exception:
        return ""


# ============================================================
# OPENROUTER CLIENT
# ============================================================

@st.cache_resource(show_spinner=False)
def get_openai_client():
    """
    Клиент создаётся один раз.
    Ошибки здесь не должны ронять страницу.
    """

    if OpenAI is None:
        return None

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return None

    try:
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=API_TIMEOUT,
            max_retries=0,
        )

    except Exception:
        return None


# ============================================================
# SAFE API CALL
# ============================================================

def safe_api_call(
    agent_key: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 12000,
) -> Optional[str]:
    """
    КРИТИЧЕСКИ ВАЖНАЯ ФУНКЦИЯ.

    Любая ошибка:
    - timeout
    - 401
    - 402
    - 403
    - 404
    - 429
    - 500
    - provider error
    - invalid JSON
    - SDK error

    не должна падать наружу.
    """

    agent = AGENTS.get(agent_key)

    if not agent:
        log(
            f"Неизвестный агент: {agent_key}",
            "error",
        )
        return None

    client = get_openai_client()

    if client is None:
        log(
            "OpenRouter client недоступен. Проверь OPENROUTER_API_KEY.",
            "error",
            agent["name"],
        )
        return None

    model = agent["model"]

    # Защита от чрезмерного prompt.
    safe_messages = []

    try:
        for msg in messages:
            role = clean_text(msg.get("role", "user"))
            content = clean_text(msg.get("content", ""))

            content = trim_text(
                content,
                MAX_PROMPT_CHARS,
            )

            safe_messages.append(
                {
                    "role": role,
                    "content": content,
                }
            )
    except Exception:
        log(
            "Не удалось подготовить messages.",
            "error",
            agent["name"],
        )
        return None

    for attempt in range(1, MAX_RETRIES_PER_CALL + 2):
        try:
            log(
                f"API request → {model} "
                f"(attempt {attempt})",
                "info",
                agent["name"],
            )

            response = client.chat.completions.create(
                model=model,
                messages=safe_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            if not response:
                raise RuntimeError(
                    "OpenRouter вернул пустой response."
                )

            choices = getattr(
                response,
                "choices",
                None,
            )

            if not choices:
                raise RuntimeEr
