from assistant.filters import apply_technical_filters
from datetime import datetime, timedelta

def test_filter_too_short():
    """Видео короче минимального порога должно быть отклонено"""
    video_data = {'duration': 10, 'upload_date': '20240101', 'width': 1280}
    assert apply_technical_filters(video_data, min_duration=180) is False

def test_filter_just_right():
    """Видео, соответствующее всем порогам, должно быть принято"""
    video_data = {'duration': 300, 'upload_date': '20240101', 'width': 1280}
    assert apply_technical_filters(video_data) is True

def test_filter_too_old():
    """Видео старше 5 лет должно быть отклонено"""
    # Дата 10 лет назад
    ten_years_ago = (datetime.now() - timedelta(days=365*10)).strftime('%Y%m%d')
    video_data = {'duration': 300, 'upload_date': ten_years_ago, 'width': 1280}
    assert apply_technical_filters(video_data, max_age_years=5) is False

def test_filter_low_resolution():
    """Видео с разрешением ниже 480p должно быть отклонено"""
    video_data = {'duration': 300, 'upload_date': '20240101', 'width': 360}
    assert apply_technical_filters(video_data, min_resolution=480) is False

def test_filter_missing_duration():
    """Видео без данных о длительности должно быть отклонено"""
    video_data = {'title': 'No duration here'}
    assert apply_technical_filters(video_data) is False
