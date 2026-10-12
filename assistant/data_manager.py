import pandas as pd
import os

def prepare_approved_row(row, start_time, end_time, audio_score, checklist_passed):
    """
    Формирует строку для сохранения в список одобренных видео.
    Соответствует формату сдачи ТЗ: Ссылка, Начало, Конец, Тематика, Аудио, Чек-лист.
    """
    data = row.to_dict() if hasattr(row, 'to_dict') else dict(row)
    data['start_time'] = start_time
    data['end_time'] = end_time
    data['audio_score'] = audio_score
    data['checklist_passed'] = "✔" if checklist_passed else "✘"
    return data
