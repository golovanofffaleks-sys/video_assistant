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
    return pd.DataFrame(columns=['title', 'duration', 'url', 'start_time', 'end_time', 'category', 'audio_score', 'checklist_passed'])

def save_data(df, file_path):
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

def main():
    st.set_page_config(page_title="AI Video Assistant", layout="wide")
    st.title("📹 AI Video Assistant")
    st.markdown("Инструмент для быстрого отбора видеоконтента")

    # Инициализация состояния очереди, если её нет
    if 'df_queue' not in st.session_state:
        st.session_state.df_queue = load_data(QUEUE_FILE)
    if 'df_approved' not in st.session_state:
        st.session_state.df_approved = load_data(APPROVED_FILE)

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
            
            st.session_state.df_queue = pd.DataFrame(filtered)
            save_data(st.session_state.df_queue, QUEUE_FILE)
            st.sidebar.success(f"Найдено {len(filtered)} видео!")

    # --- Основная область ---
    df_queue = st.session_state.df_queue
    df_approved = st.session_state.df_approved

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("📝 Очередь на проверку")
        if df_queue.empty:
            st.info("Очередь пуста. Запустите поиск в боковом меню.")
        else:
            # Используем индекс для корректного удаления
            for idx in df_queue.index:
                row = df_queue.loc[idx]
                with st.container():
                    c1, c2, c3 = st.columns([4, 2, 2])
                    c1.markdown(f"**{row['title']}**")
                    c2.write(f"⏱ {row['duration']}")
                    c3.markdown(f"[Открыть видео]({row['url']})")
                    
                    st.markdown("---")
                    
                    if f"fragments_{idx}" not in st.session_state:
                        st.session_state[f"fragments_{idx}"] = [{"start": "", "end": ""}]
                    
                    fragments = st.session_state[f"fragments_{idx}"]
                    st.markdown("**⏱ Фрагменты (таймкоды)**")
                    for f_idx, frag in enumerate(fragments):
                        f_cols = st.columns([2, 2, 1])
                        # Используем уникальные ключи, привязанные к индексу строки
                        start_val = f_cols[0].text_input("Начало", value=frag['start'], key=f"start_{idx}_{f_idx}", placeholder="00:00", label_visibility="collapsed")
                        end_val = f_cols[1].text_input("Конец", value=frag['end'], key=f"end_{idx}_{f_idx}", placeholder="00:00", label_visibility="collapsed")
                        
                        # Обновляем данные в сессии сразу
                        st.session_state[f"fragments_{idx}"][f_idx]['start'] = start_val
                        st.session_state[f"fragments_{idx}"][f_idx]['end'] = end_val
                        
                        if f_cols[2].button("🗑️", key=f"del_{idx}_{f_idx}"):
                            if len(fragments) > 1:
                                st.session_state[f"fragments_{idx}"].pop(f_idx)
                                st.rerun()

                    if st.button("➕ Добавить фрагмент", key=f"add_{idx}"):
                        st.session_state[f"fragments_{idx}"].append({"start": "", "end": ""})
                        st.rerun()

                    st.markdown("---")
                    check_col1, check_col2 = st.columns(2)
                    with check_col1:
                        st.markdown("**✅ Чек-лист**")
                        cb1 = st.checkbox("Нет музыки", key=f"cb1_{idx}")
                        cb2 = st.checkbox("Нет водяных знаков", key=f"cb2_{idx}")
                        cb3 = st.checkbox("Речь живая", key=f"cb3_{idx}")
                        cb4 = st.checkbox("Нет субтитров", key=f"cb4_{idx}")
                    with check_col2:
                        st.markdown("**🔊 Оценка аудио (1-5)**")
                        audio_score = st.slider("Качество звука", 1, 5, 3, key=f"score_{idx}")
                    
                    btn_cols = st.columns([1, 1])
                    checklist_passed = all([cb1, cb2, cb3, cb4])
                    
                    if btn_cols[0].button(f"✅ Одобрить {len(fragments)} фрагм.", key=f"app_{idx}"):
                        for frag in fragments:
                            if frag['start'] and frag['end']:
                                row_data = prepare_approved_row(row, frag['start'], frag['end'], audio_score, checklist_passed)
                                st.session_state.df_approved = pd.concat([st.session_state.df_approved, pd.DataFrame([row_data])], ignore_index=True)
                        
                        save_data(st.session_state.df_approved, APPROVED_FILE)
                        st.session_state.df_queue = df_queue.drop(idx)
                        save_data(st.session_state.df_queue, QUEUE_FILE)
                        st.rerun()
                        
                    if btn_cols[1].button(f"❌ Отклонить", key=f"rej_{idx}"):
                        st.session_state.df_queue = df_queue.drop(idx)
                        save_data(st.session_state.df_queue, QUEUE_FILE)
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
