import pandas as pd
import os

def prepare_approved_row(row, start_time, end_time):
    """
    Формирует строку для сохранения в список одобренных видео.
    Гарантирует наличие всех необходимых полей ТЗ.
    """
    data = row.to_dict() if hasattr(row, 'to_dict') else dict(row)
    data['start_time'] = start_time
    data['end_time'] = end_time
    return data
