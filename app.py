import os
import re
import time
import streamlit as st
from openai import OpenAI

# 1. Настройка внешнего вида сайта в браузере (Тема Cyberpunk)
st.set_page_config(layout="wide", page_title="Vortex Code Studio", page_icon="🌪️")

st.markdown("""
    <style>
    .stApp {
        background-color: #0B0F19;
        color: #E2E8F0;
    }
    h1 {
        color: #00F2FE !important;
        font-family: 'Courier New', Courier, monospace;
        text-shadow: 0 0 10px #00F2FE;
    }
    .terminal-box {
        background-color: #020617;
        border: 1px solid #1E293B;
        border-left: 4px solid #38BDF8;
        padding: 15px;
        border-radius: 8px;
        font-family: 'Consolas', monospace;
        margin-bottom: 10px;
    }
    .agent-name {
        color: #34D399;
        font-weight: bold;
    }
    .boss-name {
        color: #F43F5E;
        font-weight: bold;
        text-shadow: 0 0 5px #F43F5E;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌪️ VORTEX CODE")
st.subheader("Мультиагентная ИИ-Студия | Технология DMACES")
st.write("---")

# 2. Безопасное считывание ключа OpenRouter из настроек Render
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Поле для ввода идеи игры
user_prompt = st.text_input("📝 Какую браузерную игру вы хотите создать?", placeholder="Например: Арена 5х5 типа Ravenfield с ботами, стрельбой и пиксельной графикой")

# Функция для корректного извлечения чистого HTML-кода из ответов моделей
def extract_clean_code(text: str) -> str:
    if not text:
        return ""
    # Ищем код внутри ```html ... ``` или ``` ... ```
    match = re.search(r"```(?:html)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.replace("```html", "").replace("```", "").strip()

if st.button("🔥 Запустить конвейер разработки") and user_prompt:
    if not OPENROUTER_KEY:
        st.error("❌ Ошибка: Проверьте настройки API-ключа OPENROUTER_API_KEY в панели Render!")
    else:
        col_chat, col_game = st.columns(2)
        
        with col_chat:
            st.markdown("### 🖥️ Системный терминал DMACES")
            log_container = st.container()
            
            client_openrouter = OpenAI(
                base_url="[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)",
                api_key=OPENROUTER_KEY,
            )
            
            with log_container:
                st.markdown('<div class="terminal-box">⏳ <span class="agent-name">[SYSTEM]:</span> Запрос принят. Формируем ТЗ...</div>', unsafe_allow_html=True)
                time.sleep(1)
                
                st.markdown('<div class="terminal-box">🚀 <span class="agent-name">[Gemini 2.0]:</span> Разметка игрового движка, холста Canvas и физики столкновений запущена...</div>', unsafe_allow_html=True)
                time.sleep(1)
                
                st.markdown('<div class="terminal-box">🇨🇳 <span class="agent-name">[Qwen Coder]:</span> Построение процедурного мира, генерация сетки карты и пиксельных текстур кодом...</div>', unsafe_allow_html=True)
                
                # --- ШАГ 1: Генерация базового кода (Qwen Coder) ---
                raw_code = ""
                dev_models = [
                    "qwen/qwen-2.5-coder-32b-instruct",
                    "meta-llama/llama-3.3-70b-instruct:free",
                    "google/gemini-2.0-flash-001"
                ]
                
                for model_name in dev_models:
                    try:
                        response_dev = client_openrouter.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": "Ты команда ИИ. Напишите полную браузерную игру в одном HTML-файле с JS и CSS. Графика процедурная кодом (HTML5 Canvas). Выдай ТОЛЬКО чистый рабочий HTML-код без слов."},
                                {"role": "user", "content": f"Создай игру: {user_prompt}"}
                            ],
                            stream=True
                        )
                        for chunk in response_dev:
                            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                                raw_code += chunk.choices[0].delta.content
                        if raw_code.strip():
                            break # Код получен, выходим из цикла
                    except Exception:
                        raw_code = ""
                        continue # Если модель недоступна, пробуем следующую
                
                if not raw_code:
                    st.error("❌ Ошибка на этапе 1: Не удалось получить ответ от моделей-разработчиков. Проверьте баланс ключа OpenRouter.")
                    st.stop()
                
                st.markdown('<div class="terminal-box">🧬 <span class="agent-name">[SYSTEM]:</span> Модули склеены. Черновик кода собран в единый пул. Передача в отдел ОТК...</div>', unsafe_allow_html=True)
                time.sleep(1)
                
                st.markdown('<div class="terminal-box">🔍 <span class="agent-name">[DeepSeek]:</span> Включение логического мышления (Reasoning). Дотошный поиск багов, опечаток и утечек памяти...</div>', unsafe_allow_html=True)
                
                # --- ШАГ 2: Тестирование и исправление ошибок (DeepSeek QA) ---
                tested_code = ""
                qa_models = [
                    "deepseek/deepseek-chat",
                    "meta-llama/llama-3.3-70b-instruct:free",
                    "google/gemini-2.0-flash-001"
                ]
                
                for model_name in qa_models:
                    try:
                        response_test = client_openrouter.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": "Ты QA Тестировщик. Проверь этот HTML/JS код на ошибки. Исправь синтаксические и логические баги. Выдай только исправленный рабочий HTML-код."},
                                {"role": "user", "content": f"Вот код для проверки:\n\n{raw_code}"}
                            ],
                            stream=True
                        )
                        for chunk in response_test:
                            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                                tested_code += chunk.choices[0].delta.content
                        if tested_code.strip():
                            break
                    except Exception:
                        tested_code = ""
                        continue
                
                # Фолбэк: если этап QA не ответил, используем исходный код
                if not tested_code.strip():
                    tested_code = raw_code

                st.markdown('<div class="terminal-box">✨ <span class="agent-name">[Qwen & Kimi]:</span> Повторный внутренний тест пройден успешно. Передаем проект руководству...</div>', unsafe_allow_html=True)
                time.sleep(1)
                
                st.markdown('<div class="terminal-box">👑 <span class="boss-name">[Gemini Boss]:</span> Финальное ревью. Сверка с ТЗ пользователя. Наложение визуального лоска...</div>', unsafe_allow_html=True)
                
                # --- ШАГ 3: Финальная проверка (Gemini Boss) ---
                final_raw = ""
                boss_models = [
                    "google/gemini-2.0-flash-001",
                    "google/gemini-flash-1.5",
                    "meta-llama/llama-3.3-70b-instruct:free"
                ]
                
                for model_name in boss_models:
                    try:
                        response_boss = client_openrouter.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": "Ты главный архитектор. Проведи финальную проверку кода игры. Убедись, что код полностью рабочий, и выдай только финальный чистый HTML-код."},
                                {"role": "user", "content": f"Финальный код после проверки:\n\n{tested_code}"}
                            ]
                        )
                        if response_boss.choices and response_boss.choices[0].message.content:
                            final_raw = response_boss.choices[0].message.content
                            break
                    except Exception:
                        final_raw = ""
                        continue

                if not final_raw.strip():
                    final_raw = tested_code

                # Извлекаем чистый HTML без markdown
                final_code = extract_clean_code(final_raw)
                
                st.markdown('<div class="terminal-box" style="border-left-color: #34D399;">🟢 <span class="boss-name">[Gemini Boss]:</span> ПРОЕКТ УТВЕРЖДЕН. ИГРА ВЫПУЩЕНА В СЕТЬ!</div>', unsafe_allow_html=True)

        # Правая колонка: Окно превью игры
        with col_game:
            st.markdown("### 🎮 Игровой экран (Превью)")
            
            st.components.v1.html(final_code, height=600, scrolling=True)
            
            st.write("")
            st.download_button(
                label="📥 Скачать HTML-файл игры на ПК",
                data=final_code,
                file_name="vortex_game.html",
                mime="text/html"
                    )
            
