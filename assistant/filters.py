# Логика фильтрации видео
def apply_technical_filters(video_data, min_duration=15, max_duration=3600):
    """
    Проверяет видео на соответствие техническим критериям.
    Возвращает True, если видео подходит.
    """
    duration = video_data.get('duration')
    
    if duration is None:
        return False
    
    if duration < min_duration or duration > max_duration:
        return False
        
    return True
