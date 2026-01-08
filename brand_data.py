"""
Модуль для работы с данными о бренде компании.
Сохраняет и загружает профиль компании в JSON файл.
"""
import json
import os

BRAND_PROFILE_FILE = "brand_profile.json"


def load_brand_profile():
    """
    Загружает профиль бренда из файла.
    
    Returns:
        dict: Словарь с данными о бренде или пустой словарь, если файл не существует.
    """
    if os.path.exists(BRAND_PROFILE_FILE):
        try:
            with open(BRAND_PROFILE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_brand_profile(profile_data):
    """
    Сохраняет профиль бренда в файл.
    
    Args:
        profile_data (dict): Словарь с данными о бренде для сохранения.
    """
    try:
        with open(BRAND_PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def get_brand_context_string(profile_data):
    """
    Преобразует данные профиля в строку для использования в промптах AI.
    
    Args:
        profile_data (dict): Данные профиля бренда.
        
    Returns:
        str: Отформатированная строка с контекстом бренда.
    """
    if not profile_data:
        return "Информация о бренде не заполнена."
    
    context_parts = []
    
    if profile_data.get('company_name'):
        context_parts.append(f"Название компании: {profile_data['company_name']}")
    
    if profile_data.get('company_description'):
        context_parts.append(f"Описание компании: {profile_data['company_description']}")
    
    if profile_data.get('target_audience'):
        context_parts.append(f"Целевая аудитория: {profile_data['target_audience']}")
    
    if profile_data.get('tone_of_voice'):
        context_parts.append(f"Тональность общения: {profile_data['tone_of_voice']}")
    
    if profile_data.get('brand_values'):
        context_parts.append(f"Ценности бренда: {profile_data['brand_values']}")
    
    if profile_data.get('key_messages'):
        context_parts.append(f"Ключевые сообщения: {profile_data['key_messages']}")
    
    return "\n".join(context_parts) if context_parts else "Информация о бренде не заполнена."
