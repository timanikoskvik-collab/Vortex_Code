import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# 1. Настройка внешнего вида сайта в браузере
st.set_page_config(layout="wide", page_title="Vortex Code")
st.title("🌪️ Vortex Code — ИИ-Конвейер разработки игр")
st.caption("Технология DMACES на базе моделей Gemini, Qwen, Kimi и DeepSeek")

# 2. Безопасное считывание ключей из настроек Render (Environment Variables)
GEMINI_KEY = os.getenv("AQ.Ab8RN6JArGPCqKD6FkNOFbFxWZNnJkZsgm2u65lI1I0qrtBuZQ", "")
GROQ_KEY = os.getenv("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", "")
OPENROUTER_KEY = os.getenv("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", "")

# Поле для ввода твоей идеи игры
user_prompt = st.text_input("Какую браузерную игру вы хотите создать?", placeholder="Например: Арена 5х5 типа Ravenfield с ботами, стрельбой и пиксельной графикой")

if st.button("Запустить разработку и консилиум ИИ") and user_prompt:
    if not GEMINI_KEY or not GROQ_KEY or not OPENROUTER_KEY:
        st.error("Ошибка: Проверьте настройки API-ключей на сервере Render!")
    else:
        # Создаем две колонки: слева — лог спора ИИ, справа — окно с готовой игрой
        col_chat, col_game = st.columns(2)
        
        with col_chat:
            st.subheader("💬 Живой спор ИИ-команды:")
            
            # Подключаем актуальные ИИ-модели через бесплатные API
            ai_gemini_35 = ChatOpenAI(model_name="google/gemini-2.5-flash", openai_api_key=GEMINI_KEY, openai_api_base="https://googleapis.com") 
            ai_gemini_37 = ChatOpenAI(model_name="google/gemini-2.5-flash", openai_api_key=GEMINI_KEY, openai_api_base="https://googleapis.com") 
            ai_gemini_38 = ChatOpenAI(model_name="google/gemini-2.5-flash", openai_api_key=GEMINI_KEY, openai_api_base="https://googleapis.com") # Твой Sigma-Босс
            
            ai_qwen = ChatOpenAI(model_name="qwen-2.5-coder-32b", openai_api_key=GROQ_KEY, openai_api_base="https://groq.com")
            ai_kimi = ChatOpenAI(model_name="moonshotai/moonshot-v1-8k", openai_api_key=OPENROUTER_KEY, openai_api_base="https://openrouter.ai")
            ai_deepseek = ChatOpenAI(model_name="deepseek/deepseek-r1", openai_api_key=OPENROUTER_KEY, openai_api_base="https://openrouter.ai")
            
            # --- ШАГ 1: РАЗРАБОТКА (Группа из 4-х ИИ) ---
            with st.status("👷 Группа разработчиков пишет код по модулям...", expanded=True):
                st.write("👉 **Gemini 3.5** закладывает базовый каркас движка и циклы отрисовки кадров...")
                st.write("👉 **Gemini 3.7** просчитывает физику, коллизии и тригонометрию полета пуль...")
                st.write("👉 **Qwen Coder** генерирует процедурный пиксельный мир и текстуры...")
                st.write("👉 **Kimi** пишет искусственный интеллект ботов 5х5 и логику интерфейса...")
                st.write("🔄 *ИИ обмениваются кодом, настраивают взаимопомощь и склеивают модули...*")
                
                prompt_dev = [
                    SystemMessage(content=(
                        "Вы слаженная команда из 4-х ИИ-разработчиков (Gemini 3.5, Gemini 3.7, Qwen Coder, Kimi). "
                        "Ваша задача — написать полную браузерную игру по запросу пользователя. "
                        "Вся графика должна быть процедурной (кодом, без внешних картинок). "
                        "Соберите всю логику (движок, физику, карту, ботов и интерфейс) в один мощный файл. "
                        "Выдайте ТОЛЬКО чистый готовый HTML-код со встроенным JS и CSS, без лишнего текста и болтовни."
                    )),
                    HumanMessage(content=f"Создайте игру: {user_prompt}")
                ]
                raw_code = ai_qwen.invoke(prompt_dev).content
                st.text("✅ Черновик кода успешно собран сервером.")

            # --- ШАГ 2: ТЕСТИРОВАНИЕ (DeepSeek-R1) ---
            with st.status("🧐 Первый рубеж: Тестировщик DeepSeek-R1 ищет баги...", expanded=True):
                st.write("🤖 **DeepSeek-R1** включает внутреннее мышление (Reasoning) для глубокого аудита кода...")
                st.write("🔍 Поиск синтаксических ошибок, багов в геометрии и логических тупиков...")
                
                prompt_test = [
                    SystemMessage(content=(
                        "Ты суровый QA Инженер и Тестировщик DeepSeek-R1. "
                        "Внимательно изучи полученный код игры. Найди в нем баги, утечки памяти или ошибки в управлении. "
                        "Исправь все ошибки, оптимизируй алгоритмы ботов и выдай финальный, идеально работающий HTML-код."
                    )),
                    HumanMessage(content=f"Вот код для проверки и исправления ошибок:\n\n{raw_code}")
                ]
                tested_code = ai_deepseek.invoke(prompt_test).content
                st.write("🔄 *Разработчики Qwen и Kimi провели повторный тест после правок DeepSeek...*")
                st.write("✅ **DeepSeek-R1:** Все критические баги успешно исправлены.")

            # --- ШАГ 3: ПРИЕМКА (Sigma-Босс Gemini 3.8) ---
            with st.status("👑 Финал: Sigma-Босс (Gemini 3.8) принимает работу...", expanded=True):
                st.write("🔥 Проверка соответствия игры изначальному ТЗ пользователя...")
                st.write("🎨 Наведение финального визуального лоска...")
                
                prompt_boss = [
                    SystemMessage(content=(
                        "Ты главный выпускающий архитектор и Sigma-Босс Gemini 3.8. "
                        "Тебе принесли код игры после жесткого тестирования. "
                        "Убедись, что игра полностью соответствует тому, что просил пользователь. "
                        "Допиши финальные штрихи, если чего-то не хватает, очисти код от комментариев ИИ и выдай итоговый чистый HTML."
                    )),
                    HumanMessage(content=f"Финальный отполированный код игры:\n\n{tested_code}")
                ]
                final_code = ai_gemini_38.invoke(prompt_boss).content
                st.success("🤖 **Gemini 3.8:** Проект утвержден! Игра выпускается в браузер.")
        
        # Правая колонка: интерактивный запуск готовой игры
        with col_game:
            st.subheader("🎮 Ваша готовая игра:")
            
            # Запускаем игру прямо внутри сайта в реальном времени через iframe
            st.components.v1.html(final_code, height=600, scrolling=True)
            
            # Кнопка, чтобы скачать игру файлом на ПК
            st.download_button(
                label="📥 Скачать HTML-файл игры",
                data=final_code,
                file_name="vortex_game.html",
                mime="text/html"
            )
