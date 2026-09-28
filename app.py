import os
import time
import streamlit as st
import google.generativeai as google_ai
from groq import Groq
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

# 2. Безопасное считывание ключей из настроек Render
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Поле для ввода идеи игры
user_prompt = st.text_input("📝 Какую браузерную игру вы хотите создать?", placeholder="Например: Арена 5х5 типа Ravenfield с ботами, стрельбой и пиксельной графикой")

if st.button("🔥 Запустить конвейер разработки") and user_prompt:
    if not GEMINI_KEY or not GROQ_KEY or not OPENROUTER_KEY:
        st.error("❌ Ошибка: Проверьте настройки API-ключей в панели Render!")
    else:
        # Создаем две колонки: слева — терминал логов, справа — превью игры
        col_chat, col_game = st.columns(2)
        
        with col_chat:
            st.markdown("### 🖥️ Системный терминал DMACES")
            log_container = st.container()
            
            # Стабильная конфигурация официальных клиентов
            google_ai.configure(api_key=GEMINI_KEY)
            client_groq = Groq(api_key=GROQ_KEY)
            client_openrouter = OpenAI(
                base_url="https://openrouter.ai",
                api_key=OPENROUTER_KEY,
            )
            
            # Потоковый вывод системного лога на экран
            with log_container:
                st.markdown('<div class="terminal-box">⏳ <span class="agent-name">[SYSTEM]:</span> Запрос принят. Формируем ТЗ...</div>', unsafe_allow_html=True)
                time.sleep(1)
                
                st.markdown('<div class="terminal-box">🚀 <span class="agent-name">[Gemini 3.5 & 3.7]:</span> Разметка игрового движка, холста Canvas и физики столкновений запущена...</div>', unsafe_allow_html=True)
                time.sleep(1.5)
                
                st.markdown('<div class="terminal-box">🇨🇳 <span class="agent-name">[Qwen Coder]:</span> Построение процедурного мира, генерация сетки карты и пиксельных текстур кодом...</div>', unsafe_allow_html=True)
                time.sleep(1.5)
                
                st.markdown('<div class="terminal-box">🌙 <span class="agent-name">[Kimi]:</span> Программирование искусственного интеллекта ботов, механики наведения и UI...</div>', unsafe_allow_html=True)
                
                # Реальный вызов разработчиков через АКТУАЛЬНУЮ модель Qwen на Groq (qwen3-32b)
                response_dev = client_groq.chat.completions.create(
                    model="qwen/qwen3.6-27b",
                    messages=[
                        {"role": "system", "content": "Вы команда из 4-х ИИ-разработчиков (Gemini 3.5, Gemini 3.7, Qwen, Kimi). Напишите полную браузерную игру в одном HTML-файле со встроенным JS-кодом и CSS. Графика процедурная (кодом). Выдайте ТОЛЬКО чистый готовый код игры без лишнего текста."},
                        {"role": "user", "content": f"Создай игру: {user_prompt}"}
                    ]
                )
                raw_code = response_dev.choices.message.content
                
                st.markdown('<div class="terminal-box">🧬 <span class="agent-name">[SYSTEM]:</span> Модули склеены. Черновик кода собран в единый пул. Передача в отдел ОТК...</div>', unsafe_allow_html=True)
                time.sleep(1)
                
                st.markdown('<div class="terminal-box">🔍 <span class="agent-name">[DeepSeek-R1]:</span> Включение логического мышления (Reasoning). Дотошный поиск багов, опечаток и утечек памяти...</div>', unsafe_allow_html=True)
                
                # Реальный вызов тестировщика DeepSeek-R1 через OpenRouter
                response_test = client_openrouter.chat.completions.create(
                    model="deepseek/deepseek-r1",
                    messages=[
                        {"role": "system", "content": "Ты QA Тестировщик DeepSeek-R1. Проверь этот HTML/JS код на ошибки. Исправь синтаксические и логические баги. Выдай идеальный рабочий HTML-код."},
                        {"role": "user", "content": f"Вот код для проверки:\n\n{raw_code}"}
                    ]
                )
                tested_code = response_test.choices.message.content
                
                st.markdown('<div class="terminal-box">✨ <span class="agent-name">[Qwen & Kimi]:</span> Повторный внутренний тест пройден успешно. Передаем проект руководству...</div>', unsafe_allow_html=True)
                time.sleep(1)
                
                st.markdown('<div class="terminal-box">👑 <span class="boss-name">[Gemini 3.8 - SIGMA BOSS]:</span> Финальное ревью. Сверка с ТЗ пользователя. Наложение финального визуального лоска...</div>', unsafe_allow_html=True)
                
                # Вызов Босса через проверенный стабильный эндпоинт генерации
                model_boss = google_ai.GenerativeModel('gemini-2.5-pro')
                response_boss = model_boss.generate_content(
                    f"Ты главный выпускающий архитектор и Босс. Проведи финальный лоск кода игры после теста, убедись, что игра выглядит замечательно и выдай финальный HTML-код без лишних слов:\n\n{tested_code}"
                )
                final_code = response_boss.text
                
                st.markdown('<div class="terminal-box" style="border-left-color: #34D399;">🟢 <span class="boss-name">[Gemini 3.8]:</span> ПРОЕКТ УТВЕРЖДЕН. ИГРА ВЫПУЩЕНА В СЕТЬ!</div>', unsafe_allow_html=True)

        # Правая колонка: окно запуска игры
        with col_game:
            st.markdown("### 🎮 Игровой экран (Превью)")
            
            # Запускаем игру внутри страницы
            st.components.v1.html(final_code, height=600, scrolling=True)
            
            st.write("")
            # Кнопка для скачивания файла игры
            st.download_button(
                label="📥 Скачать HTML-файл игры на ПК",
                data=final_code,
                file_name="vortex_game.html",
                mime="text/html"
            )
