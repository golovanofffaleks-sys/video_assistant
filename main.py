import csv
from assistant.searcher import fetch_videos
from assistant.filters import apply_technical_filters

def run_assistant(query, min_duration=15, max_results=50):
    print(f"🚀 Запуск ассистента по запросу: {query}")
    
    # 1. Поиск
    raw_videos = fetch_videos(query, max_results)
    print(f"📦 Найдено сырых данных: {len(raw_videos)}")
    
    # 2. Фильтрация
    final_list = []
    for video in raw_videos:
        if apply_technical_filters(video, min_duration=min_duration):
            # Форматируем данные для таблицы
            duration_sec = video.get('duration', 0)
            duration_str = f"{duration_sec // 60}:{duration_sec % 60:02d}"
            
            final_list.append({
                'title': video.get('title', 'Без названия'),
                'duration': duration_str,
                'url': f"https://www.youtube.com/watch?v={video.get('id')}"
            })
    
    print(f"✅ После фильтрации осталось: {len(final_list)}")
    
    # 3. Сохранение
    filename = "filtered_videos.csv"
    with open(filename, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'duration', 'url'])
        writer.writeheader()
        writer.writerows(final_list)
    
    print(f"💾 Результаты сохранены в {filename}")

if __name__ == "__main__":
    # Настройки поиска
    SEARCH_QUERY = "как собрать мебель"
    MIN_DURATION = 20 # секунд
    MAX_RESULTS = 100
    
    run_assistant(SEARCH_QUERY, min_duration=MIN_DURATION, max_results=MAX_RESULTS)
