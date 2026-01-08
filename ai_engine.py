"""
Модуль для работы с Google Gemini API.
Генерирует идеи и контент на основе профиля бренда.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from brand_data import get_brand_context_string

# Загружаем переменные окружения из различных источников
# Приоритет: env.local > .env.local > .env > системные переменные
# Также поддерживаем переменные окружения Streamlit Cloud
env_files = ['env.local', '.env.local', '.env']
api_key = None

# Сначала пробуем файлы (для локальной разработки)
for env_file in env_files:
    if os.path.exists(env_file):
        load_dotenv(env_file, override=True)
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and len(api_key) > 10:  # Проверяем, что ключ не пустой
            break

# Если не нашли в файлах, пробуем системные переменные (для Streamlit Cloud)
if not api_key or len(api_key) <= 10:
    load_dotenv()  # Загружает из .env по умолчанию
    api_key = os.getenv('GEMINI_API_KEY')

# Инициализация Gemini
if api_key:
    genai.configure(api_key=api_key)
else:
    genai.configure(api_key=None)


def get_gemini_model():
    """
    Автоматически находит доступную модель Gemini для генерации контента.
    
    Returns:
        GenerativeModel: Инициализированная модель или None, если не найдена.
    """
    if not api_key:
        return None
    
    # Приоритетный список моделей - Gemini 2.5 Pro (основная) и 2.5 Flash (запасная)
    preferred_models = [
        'gemini-2.5-pro',      # Основная модель - самая мощная
        'gemini-2.5-flash',    # Запасная модель - быстрая альтернатива
        'gemini-1.5-pro',      # Fallback варианты
        'gemini-1.5-flash',
        'gemini-2.0-flash-exp',
        'gemini-1.0-pro',
        'gemini-pro',
    ]
    
    # Сначала пробуем получить список доступных моделей через API
    try:
        available_models = genai.list_models()
        
        # Фильтруем модели, которые поддерживают generateContent
        supported_models = []
        for model in available_models:
            # Проверяем, что модель поддерживает generateContent
            if hasattr(model, 'supported_generation_methods') and model.supported_generation_methods:
                if 'generateContent' in model.supported_generation_methods:
                    # Извлекаем имя модели (убираем префикс 'models/')
                    model_name = model.name
                    if model_name.startswith('models/'):
                        model_name = model_name.replace('models/', '')
                    supported_models.append(model_name)
        
        # Ищем модели из приоритетного списка (2.5 Pro и 2.5 Flash)
        for preferred in preferred_models:
            for supported in supported_models:
                # Проверяем точное совпадение или частичное (например, "gemini-2.5-pro" в "models/gemini-2.5-pro")
                if preferred == supported or supported.endswith(preferred) or preferred in supported:
                    try:
                        return genai.GenerativeModel(preferred)
                    except Exception:
                        # Если не получилось с коротким именем, пробуем полное
                        try:
                            return genai.GenerativeModel(supported)
                        except Exception:
                            continue
        
        # Ищем модель из приоритетного списка
        for preferred in preferred_models:
            # Проверяем точное совпадение или частичное
            for supported in supported_models:
                if preferred == supported or supported.endswith(preferred):
                    try:
                        model_instance = genai.GenerativeModel(preferred)
                        return model_instance
                    except Exception as e:
                        # Если не получилось, пробуем с полным именем
                        try:
                            return genai.GenerativeModel(supported)
                        except Exception:
                            continue
        
        # Если не нашли приоритетную, берем первую доступную
        if supported_models:
            for model_name in supported_models:
                try:
                    return genai.GenerativeModel(model_name)
                except Exception:
                    continue
    except Exception as e:
        # Если не удалось получить список моделей, пробуем стандартные имена
        pass
    
    # Fallback: пробуем модели из приоритетного списка напрямую
    # Сначала пробуем основные модели (2.5 Pro и 2.5 Flash)
    for model_name in preferred_models:
        try:
            model_instance = genai.GenerativeModel(model_name)
            return model_instance
        except Exception:
            continue
    
    return None


# Инициализируем модель (будет переинициализирована при необходимости)
_model_instance = None

def get_model():
    """
    Получает модель Gemini, переинициализируя при необходимости.
    
    Returns:
        GenerativeModel: Инициализированная модель или None.
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = get_gemini_model()
    return _model_instance


def check_api_key():
    """Проверяет, установлен ли API ключ."""
    return api_key is not None and api_key != "your_api_key_here"


def generate_ideas(brand_profile, count=5):
    """
    Генерирует идеи для контента на основе профиля бренда.
    
    Args:
        brand_profile (dict): Профиль бренда.
        count (int): Количество идей для генерации (по умолчанию 5).
        
    Returns:
        list: Список идей или сообщение об ошибке.
    """
    if not check_api_key():
        return ["Ошибка: API ключ не установлен. Проверьте файлы .env, .env.local или env.local"]
    
    model = get_model()
    if not model:
        return ["Ошибка: Модель не инициализирована. Проверьте API ключ и доступность моделей Gemini."]
    
    brand_context = get_brand_context_string(brand_profile)
    
    prompt = f"""Ты - эксперт по контент-маркетингу. На основе следующей информации о бренде, придумай {count} креативных идей для контента (посты, статьи, видео и т.д.).

Информация о бренде:
{brand_context}

Требования:
- Идеи должны быть релевантны целевой аудитории
- Учитывай тональность и ценности бренда
- Идеи должны быть практичными и реализуемыми
- Разнообразь форматы (текст, видео, инфографика и т.д.)

Верни список из {count} идей. Каждая идея должна быть на отдельной строке и начинаться с номера (1., 2., 3. и т.д.).
Будь конкретным и креативным."""

    try:
        response = model.generate_content(prompt)
        ideas_text = response.text.strip()
        
        # Разбиваем на отдельные идеи
        ideas = [idea.strip() for idea in ideas_text.split('\n') if idea.strip() and (idea.strip()[0].isdigit() or idea.strip().startswith('-'))]
        
        # Если не получилось разбить, возвращаем весь текст
        if not ideas:
            ideas = [ideas_text]
        
        return ideas[:count] if len(ideas) > count else ideas
    except Exception as e:
        return [f"Ошибка при генерации идей: {str(e)}"]


def generate_post(brand_profile, topic, platform="instagram", length="short"):
    """
    Генерирует готовый пост на основе темы и профиля бренда.
    
    Args:
        brand_profile (dict): Профиль бренда.
        topic (str): Тема поста.
        platform (str): Платформа для поста (instagram, facebook, telegram, blog).
        length (str): Длина поста (short, medium, long).
        
    Returns:
        str: Сгенерированный текст поста или сообщение об ошибке.
    """
    if not check_api_key():
        return "Ошибка: API ключ не установлен. Проверьте файлы .env, .env.local или env.local"
    
    model = get_model()
    if not model:
        return "Ошибка: Модель не инициализирована. Проверьте API ключ и доступность моделей Gemini."
    
    brand_context = get_brand_context_string(brand_profile)
    
    # Определяем требования к длине
    length_requirements = {
        "short": "короткий пост (2-3 предложения, до 150 слов)",
        "medium": "средний пост (4-6 предложений, 150-300 слов)",
        "long": "длинный пост (7+ предложений, 300+ слов)"
    }
    
    # Определяем особенности платформы
    platform_notes = {
        "instagram": "Используй эмодзи, хештеги в конце, короткие абзацы. Стиль должен быть визуальным и вовлекающим.",
        "facebook": "Более развернутый формат, можно использовать списки. Подходит для более детального контента.",
        "telegram": "Неформальный стиль, можно использовать эмодзи. Хорошо подходят короткие абзацы.",
        "blog": "Развернутый формат, структурированный текст с подзаголовками, списками. Более формальный стиль."
    }
    
    prompt = f"""Ты - профессиональный копирайтер. Напиши пост для {platform} на тему "{topic}".

Информация о бренде:
{brand_context}

Требования к посту:
- Длина: {length_requirements.get(length, length_requirements['medium'])}
- Платформа: {platform}
- {platform_notes.get(platform, '')}
- Соблюдай тональность бренда
- Обращайся к целевой аудитории
- Включи призыв к действию (CTA)
- Пост должен быть интересным и полезным

Напиши готовый пост, который можно сразу публиковать."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Ошибка при генерации поста: {str(e)}"


def generate_content_plan(brand_profile, period="week", count=7):
    """
    Генерирует контент-план на указанный период.
    
    Args:
        brand_profile (dict): Профиль бренда.
        period (str): Период планирования (week, month).
        count (int): Количество дней/постов в плане.
        
    Returns:
        str: Сгенерированный контент-план или сообщение об ошибке.
    """
    if not check_api_key():
        return "Ошибка: API ключ не установлен. Проверьте файлы .env, .env.local или env.local"
    
    model = get_model()
    if not model:
        return "Ошибка: Модель не инициализирована. Проверьте API ключ и доступность моделей Gemini."
    
    brand_context = get_brand_context_string(brand_profile)
    
    period_name = "неделю" if period == "week" else "месяц"
    
    prompt = f"""Ты - эксперт по контент-планированию. Создай детальный контент-план на {period_name} ({count} постов) для бренда.

Информация о бренде:
{brand_context}

Требования:
- Создай план на {count} дней
- Для каждого дня укажи: дату/день недели, тему поста, формат (текст/видео/инфографика), краткое описание
- Темы должны быть разнообразными и релевантными
- Учитывай целевую аудиторию и ценности бренда
- Распредели контент равномерно по дням

Верни структурированный план в формате:
День 1 (Понедельник):
Тема: [тема]
Формат: [формат]
Описание: [краткое описание]

И так далее для всех дней."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Ошибка при генерации контент-плана: {str(e)}"
