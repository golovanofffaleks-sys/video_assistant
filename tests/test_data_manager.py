from assistant.data_manager import prepare_approved_row

def test_prepare_approved_row_success():
    """Проверка корректного формирования строки одобренного видео"""
    row = {'title': 'Test Video', 'duration': '10:00', 'url': 'http://yt.com/1', 'category': 'кулинария'}
    start = '01:00'
    end = '05:00'
    
    result = prepare_approved_row(row, start, end)
    
    assert result['title'] == 'Test Video'
    assert result['start_time'] == '01:00'
    assert result['end_time'] == '05:00'
    assert result['category'] == 'кулинария'

def test_prepare_approved_row_empty_times():
    """Проверка работы с пустыми таймкодами"""
    row = {'title': 'Test Video', 'duration': '10:00', 'url': 'http://yt.com/1', 'category': 'DIY'}
    
    result = prepare_approved_row(row, '', '')
    
    assert result['start_time'] == ''
    assert result['end_time'] == ''
