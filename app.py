import streamlit as st
import pandas as pd
import os
from assistant.searcher import fetch_videos
from assistant.filters import apply_technical_filters
from assistant.data_manager import prepare_approved_row

# Константы файлов
QUEUE_FILE = "queue.csv"
APPROVED_FILE = "approved.csv"

def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=['title', 'duration', 'url', 'start_time', 'end_time', 'category'])

def save_data(df, file_path):
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

def main():
    st.set_page_config(page_title="AI Video Assistant", layout="wide")
    st.title("📹 AI Video Assistant")
    st.markdown("Инструмент для быстрого отбора видеоконтента")

    # --- Сайдбар: Настройки и Поиск ---
    st.sidebar.header("⚙️ Настройки")
    category = st.sidebar.selectbox("Тематика", ["кулинария", "обзоры техники", "DIY/ремонт", "трэвел-блоги"])
    query = st.sidebar.text_input("Поисковый запрос", value=category)
    min_dur = st.sidebar.number_input("Мин. длительность (сек)", value=180) # 3 минуты по ТЗ
    max_res = st.sidebar.slider("Кол-во результатов", 10, 500, 100)
    
    if st.sidebar.button("🔍 Начать поиск"):
        with st.spinner("Собираем видео..."):
            raw_videos = fetch_videos(query, max_results=max_res)
            filtered = []
            for v in raw_videos:
                if apply_technical_filters(v, min_duration=min_dur):
                    duration_sec = v.get('duration', 0)
                    filtered.append({
                        'title': v.get('title', 'Без названия'),
                        'duration': f"{duration_sec // 60}:{duration_sec % 60:02d}",
                        'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                        'start_time': '',
                        'end_time': '',
                        'category': category
                    })
            
            # Сохраняем в очередь
            df_queue = pd.DataFrame(filtered)
            save_data(df_queue, QUEUE_FILE)
            st.sidebar.success(f"Найдено {len(filtered)} видео!")

    # --- Основная область ---
    # Загружаем данные
    df_queue = load_data(QUEUE_FILE)
    df_approved = load_data(APPROVED_FILE)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("📝 Очередь на проверку")
        if df_queue.empty:
            st.info("Очередь пуста. Запустите поиск в боковом меню.")
        else:
            # Отображаем видео одно за другим для удобства (или таблицей)
            for idx, row in df_queue.iterrows():
                with st.container():
                    c1, c2, c3 = st.columns([4, 2, 2])
                    c1.markdown(f"**{row['title']}**")
                    c2.write(f"⏱ {row['duration']}")
                    
                    # Кнопка ссылки
                    c3.markdown(f"[Открыть видео]({row['url']})")
                    
                    # Поля для таймкодов
                    t_cols = st.columns([2, 2])
                    start_t = t_cols[0].text_input("Начало", key=f"start_{idx}", placeholder="00:00", label_visibility="collapsed")
                    end_t = t_cols[1].text_input("Конец", key=f"end_{idx}", placeholder="00:00", label_visibility="collapsed")
                    
                    # Кнопки действий
                    btn_cols = st.columns([1, 1])
                    if btn_cols[0].button(f"✅ Подходит", key=f"app_{idx}"):
                        # Используем протестированную функцию для подготовки данных
                        row_data = prepare_approved_row(row, start_t, end_t)
                        
                        # Добавляем в одобренные
                        df_approved = pd.concat([df_approved, pd.DataFrame([row_data])], ignore_index=True)
                        save_data(df_approved, APPROVED_FILE)
                        # Удаляем из очереди
                        df_queue = df_queue.drop(idx)
                        save_data(df_queue, QUEUE_FILE)
                        st.rerun()
                        
                    if btn_cols[1].button(f"❌ Нет", key=f"rej_{idx}"):
                        # Просто удаляем из очереди
                        df_queue = df_queue.drop(idx)
                        save_data(df_queue, QUEUE_FILE)
                        st.rerun()
                    st.divider()

    with col2:
        st.subheader("📊 Статистика")
        st.metric("Одобрено", len(df_approved))
        st.metric("Осталось", len(df_queue))
        
        st.divider()
        
        if not df_approved.empty:
            st.markdown("### 💾 Экспорт")
            csv_data = df_approved.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="Скачать финальный список (CSV)",
                data=csv_data,
                file_name="final_approved_videos.csv",
                mime="text/csv"
            )
            
            if st.button("🗑️ Очистить одобренные"):
                if os.path.exists(APPROVED_FILE):
                    os.remove(APPROVED_FILE)
                    st.rerun()

if __name__ == "__main__":
    main()
