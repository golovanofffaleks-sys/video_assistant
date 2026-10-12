# Логика фильтрации видео
def apply_technical_filters(video_data, min_duration=15, max_duration=3600):
    duration = video_data.get('duration')
    if duration is None:
        return False
    return min_duration <= duration <= max_duration
