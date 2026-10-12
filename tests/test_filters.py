from assistant.filters import apply_technical_filters

def test_filter_too_short():
    """Видео короче минимального порога должно быть отклонено"""
    video_data = {'duration': 10} # 10 < 15
    assert apply_technical_filters(video_data, min_duration=15) is False

def test_filter_just_right():
    """Видео, соответствующее порогу, должно быть принято"""
    video_data = {'duration': 20} # 20 > 15
    assert apply_technical_filters(video_data, min_duration=15) is True

def test_filter_missing_duration():
    """Видео без данных о длительности должно быть отклонено"""
    video_data = {'title': 'No duration here'}
    assert apply_technical_filters(video_data, min_duration=15) is False

def test_filter_too_long():
    """Видео длиннее максимального порога должно быть отклонено"""
    video_data = {'duration': 5000} # 5000 > 3600
    assert apply_technical_filters(video_data, max_duration=3600) is False
