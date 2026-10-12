import pytest
from unittest.mock import patch, MagicMock
from assistant.searcher import fetch_videos

def test_fetch_videos_success():
    """Проверка успешного извлечения списка видео"""
    # Создаем имитацию (mock) для YoutubeDL
    mock_entries = [
        {'id': '123', 'title': 'Video 1', 'duration': 100},
        {'id': '456', 'title': 'Video 2', 'duration': 200},
    ]
    mock_response = {'entries': mock_entries}

    # Подменяем YoutubeDL.YoutubeDL так, чтобы метод extract_info возвращал наш mock_response
    with patch('yt_dlp.YoutubeDL') as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = mock_response
        
        results = fetch_videos("test query", max_results=2)
        
        assert len(results) == 2
        assert results[0]['id'] == '123'
        assert results[1]['title'] == 'Video 2'

def test_fetch_videos_empty():
    """Проверка поведения при пустых результатах поиска"""
    mock_response = {'entries': []}

    with patch('yt_dlp.YoutubeDL') as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = mock_response
        
        results = fetch_videos("nothing", max_results=10)
        
        assert results == []

def test_fetch_videos_error():
    """Проверка поведения при ошибке API/Сети"""
    with patch('yt_dlp.YoutubeDL') as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.side_effect = Exception("Network Error")
        
        # Мы ожидаем, что функция не упадет с ошибкой, а вернет пустой список (или обработает ошибку)
        results = fetch_videos("error query")
        
        assert results == []
