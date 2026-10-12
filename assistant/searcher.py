import yt_dlp

def fetch_videos(query, max_results=50):
    """
    Поиск видео по запросу через yt-dlp.
    """
    ydl_opts = {
        'quiet': True, 
        'extract_flat': True, 
        'force_generic_extractor': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Поиск через префикс ytsearch (для YouTube)
        # Для VK или других платформ потребуется иная логика или URL
        search_results = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
        
        if 'entries' not in search_results:
            return []
            
        return search_results['entries']
