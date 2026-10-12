# Логика фильтрации видео
def apply_technical_filters(video_data, min_duration=180, max_duration=600, max_age_years=5, min_resolution=480):
    """
    Комплексная проверка видео на соответствие ТЗ.
    Возвращает True, если видео подходит по всем техническим параметрам.
    """
    # 1. Проверка длительности
    duration = video_data.get('duration')
    if duration is None or not (min_duration <= duration <= max_duration):
        return False

    # 2. Проверка даты (max_age_years)
    # Ожидаем upload_date в формате 'YYYYMMDD' (стандарт yt-dlp)
    upload_date_str = video_data.get('upload_date')
    if upload_date_str:
        try:
            from datetime import datetime
            upload_date = datetime.strptime(upload_date_str, '%Y%m%d')
            years_diff = (datetime.now() - upload_date).days / 365.25
            if years_diff > max_age_years:
                return False
        except ValueError:
            return False # Если дата в странном формате, перестраховываемся

    # 3. Проверка разрешения (min_resolution)
    # В extract_flat данные о разрешении могут отсутствовать.
    # В реальном поиске разрешение проверяется через width/height.
    width = video_data.get('width')
    if width and width < min_resolution:
        return False

    return True
