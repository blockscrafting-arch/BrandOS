"""
BrandOS - Приложение для генерации контента на основе профиля бренда.
Главный файл приложения с интерфейсом на Streamlit.
"""
import streamlit as st
from brand_data import load_brand_profile, save_brand_profile, get_brand_context_string
from ai_engine import generate_ideas, generate_post, generate_content_plan, check_api_key

# Настройка страницы
st.set_page_config(
    page_title="BrandOS - Генератор контента",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Инициализация состояния сессии
if 'brand_profile' not in st.session_state:
    st.session_state.brand_profile = load_brand_profile()

# Заголовок приложения
st.title("🚀 BrandOS")
st.markdown("### Генератор контента на основе профиля вашего бренда")

# Проверка API ключа
if not check_api_key():
    st.error("⚠️ API ключ не установлен!")
    st.markdown("""
    **Создайте один из файлов в корне проекта:**
    - `.env` 
    - `.env.local`
    - `env.local`
    
    И добавьте строку: `GEMINI_API_KEY=ваш_ключ`
    
    Приложение автоматически найдет ключ в любом из этих файлов.
    """)
    st.stop()

# Боковая панель с информацией
with st.sidebar:
    st.header("ℹ️ О приложении")
    st.markdown("""
    **BrandOS** помогает создавать контент для вашего бренда:
    
    - 📝 Генерация идей
    - ✍️ Написание постов
    - 📅 Создание контент-планов
    
    Заполните профиль бренда, и AI будет создавать контент в вашем стиле!
    """)
    
    # Показываем текущий профиль
    if st.session_state.brand_profile:
        st.success("✅ Профиль бренда загружен")
        if st.button("🔄 Обновить профиль"):
            st.session_state.brand_profile = load_brand_profile()
            st.rerun()
    else:
        st.warning("⚠️ Профиль бренда не заполнен")

# Основные вкладки
tab1, tab2, tab3, tab4 = st.tabs(["📋 Профиль бренда", "💡 Брейншторм", "✍️ Генератор постов", "📅 Контент-план"])

# Вкладка 1: Профиль бренда
with tab1:
    st.header("Настройка профиля бренда")
    st.markdown("Заполните информацию о вашей компании. Это поможет AI создавать релевантный контент.")
    
    # Поля для ввода данных
    company_name = st.text_input(
        "Название компании",
        value=st.session_state.brand_profile.get('company_name', ''),
        help="Официальное название вашей компании"
    )
    
    company_description = st.text_area(
        "Описание компании",
        value=st.session_state.brand_profile.get('company_description', ''),
        height=100,
        help="Чем занимается ваша компания? Что вы предлагаете?"
    )
    
    target_audience = st.text_area(
        "Целевая аудитория",
        value=st.session_state.brand_profile.get('target_audience', ''),
        height=80,
        help="Опишите вашу целевую аудиторию: возраст, интересы, потребности"
    )
    
    tone_of_voice = st.text_area(
        "Тональность общения",
        value=st.session_state.brand_profile.get('tone_of_voice', ''),
        height=80,
        help="Как вы общаетесь с клиентами? (дружелюбно, профессионально, неформально и т.д.)"
    )
    
    brand_values = st.text_area(
        "Ценности бренда",
        value=st.session_state.brand_profile.get('brand_values', ''),
        height=80,
        help="Какие ценности важны для вашего бренда?"
    )
    
    key_messages = st.text_area(
        "Ключевые сообщения",
        value=st.session_state.brand_profile.get('key_messages', ''),
        height=80,
        help="Основные сообщения, которые вы хотите донести до аудитории"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("💾 Сохранить профиль", type="primary"):
            profile_data = {
                'company_name': company_name,
                'company_description': company_description,
                'target_audience': target_audience,
                'tone_of_voice': tone_of_voice,
                'brand_values': brand_values,
                'key_messages': key_messages
            }
            
            if save_brand_profile(profile_data):
                st.session_state.brand_profile = profile_data
                st.success("✅ Профиль успешно сохранен!")
                st.rerun()
            else:
                st.error("❌ Ошибка при сохранении профиля")
    
    # Показываем текущий контекст
    if st.session_state.brand_profile:
        with st.expander("📄 Просмотр текущего профиля"):
            st.text(get_brand_context_string(st.session_state.brand_profile))

# Вкладка 2: Брейншторм
with tab2:
    st.header("💡 Генератор идей")
    st.markdown("AI придумает креативные идеи для контента на основе вашего профиля бренда.")
    
    if not st.session_state.brand_profile or not any(st.session_state.brand_profile.values()):
        st.warning("⚠️ Сначала заполните профиль бренда во вкладке 'Профиль бренда'")
    else:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            idea_count = st.number_input("Количество идей", min_value=3, max_value=10, value=5)
        
        if st.button("🎯 Придумать идеи", type="primary"):
            with st.spinner("🤔 Генерирую идеи..."):
                ideas = generate_ideas(st.session_state.brand_profile, count=idea_count)
                
                if ideas:
                    st.success(f"✅ Сгенерировано {len(ideas)} идей!")
                    
                    for i, idea in enumerate(ideas, 1):
                        with st.container():
                            st.markdown(f"### 💡 Идея {i}")
                            st.write(idea)
                            st.divider()

# Вкладка 3: Генератор постов
with tab3:
    st.header("✍️ Генератор постов")
    st.markdown("Создайте готовый пост на любую тему в стиле вашего бренда.")
    
    if not st.session_state.brand_profile or not any(st.session_state.brand_profile.values()):
        st.warning("⚠️ Сначала заполните профиль бренда во вкладке 'Профиль бренда'")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input(
                "Тема поста",
                placeholder="Например: Новый продукт, Полезный совет, История успеха...",
                help="О чем будет пост?"
            )
            
            platform = st.selectbox(
                "Платформа",
                options=["instagram", "facebook", "telegram", "blog"],
                help="Для какой платформы создаем пост?"
            )
        
        with col2:
            length = st.selectbox(
                "Длина поста",
                options=["short", "medium", "long"],
                format_func=lambda x: {
                    "short": "Короткий (2-3 предложения)",
                    "medium": "Средний (4-6 предложений)",
                    "long": "Длинный (7+ предложений)"
                }[x],
                help="Какой длины должен быть пост?"
            )
        
        if st.button("✨ Сгенерировать пост", type="primary"):
            if not topic:
                st.error("⚠️ Введите тему поста")
            else:
                with st.spinner("✍️ Пишу пост..."):
                    post_text = generate_post(
                        st.session_state.brand_profile,
                        topic,
                        platform,
                        length
                    )
                    
                    if post_text and not post_text.startswith("Ошибка"):
                        st.success("✅ Пост готов!")
                        st.text_area(
                            "Ваш пост:",
                            value=post_text,
                            height=300,
                            label_visibility="collapsed"
                        )
                        
                        # Кнопка для копирования
                        st.code(post_text, language=None)
                    else:
                        st.error(post_text)

# Вкладка 4: Контент-план
with tab4:
    st.header("📅 Генератор контент-плана")
    st.markdown("Создайте план публикаций на неделю или месяц.")
    
    if not st.session_state.brand_profile or not any(st.session_state.brand_profile.values()):
        st.warning("⚠️ Сначала заполните профиль бренда во вкладке 'Профиль бренда'")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            period = st.selectbox(
                "Период",
                options=["week", "month"],
                format_func=lambda x: "Неделя" if x == "week" else "Месяц",
                help="На какой период создаем план?"
            )
        
        with col2:
            post_count = st.number_input(
                "Количество постов",
                min_value=3,
                max_value=30,
                value=7 if period == "week" else 15,
                help="Сколько постов включить в план?"
            )
        
        if st.button("📅 Создать контент-план", type="primary"):
            with st.spinner("📋 Создаю контент-план..."):
                plan = generate_content_plan(
                    st.session_state.brand_profile,
                    period,
                    post_count
                )
                
                if plan and not plan.startswith("Ошибка"):
                    st.success("✅ Контент-план готов!")
                    st.text_area(
                        "Ваш контент-план:",
                        value=plan,
                        height=500,
                        label_visibility="collapsed"
                    )
                    
                    # Кнопка для копирования
                    st.code(plan, language=None)
                else:
                    st.error(plan)

# Футер
st.divider()
st.markdown(
    "<div style='text-align: center; color: gray;'>BrandOS MVP - Генератор контента на основе AI</div>",
    unsafe_allow_html=True
)
