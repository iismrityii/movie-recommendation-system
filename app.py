import os
import pickle
from pathlib import Path
import gdown
import random

import pandas as pd
import requests
import streamlit as st

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

# ============================================================================
# PREMIUM CINEMATIC CONFIGURATION
# ============================================================================
PREMIUM_COLORS = {
    "dark_bg": "#030b14",          # Deep midnight blue
    "card_bg": "rgba(10, 20, 35, 0.4)", # Glassmorphism base
    "secondary_bg": "#060f1c",     # Slightly lighter
    "primary_accent": "#d4af37",   # Soft gold
    "accent_purple": "#c5a017",    # Darker gold for gradients
    "text_primary": "#fdfdfd",
    "text_secondary": "#b0c4de",
    "gold": "#d4af37",
}

TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
FALLBACK_POSTER = "https://placehold.co/500x750/1a1a1a/ffffff?text=No+Poster"

FILE_ID = "1TPM1vM1UqpZEOYXpIugNtpJddPj6Yo9n"  # Google Drive file ID for similarity.pkl

# ============================================================================
# DATA LOADING FUNCTIONS (UNCHANGED FROM ORIGINAL)
# ============================================================================
def download_similarity():
    if not os.path.exists("similarity.pkl"):
        url = f"https://drive.google.com/uc?id={FILE_ID}"
        gdown.download(url, "similarity.pkl", quiet=False)


@st.cache_data(show_spinner=False)
def load_movies() -> pd.DataFrame:
    with open("movie_dict.pkl", "rb") as f:
        movies_dict = pickle.load(f)
    return pd.DataFrame(movies_dict)


@st.cache_data(show_spinner=False)
def load_similarity():
    download_similarity()
    with open("similarity.pkl", "rb") as f:
        return pickle.load(f)


def get_api_key() -> str:
    try:
        return st.secrets["TMDB_API_KEY"]
    except Exception:
        if load_dotenv is not None:
            load_dotenv()
        return os.getenv("TMDB_API_KEY", "")


# ============================================================================
# RECOMMENDATION ENGINE (CACHED FOR PERFORMANCE)
# ============================================================================

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_poster(movie_id: int, api_key: str) -> str:
    if not api_key:
        st.error("No API Key Found")
        return FALLBACK_POSTER

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": api_key}

    try:
        response = requests.get(url, params=params, timeout=15)

        if response.status_code == 200:
            data = response.json()

            poster_path = data.get("poster_path")

            if poster_path:
                return f"{TMDB_IMAGE_BASE_URL}{poster_path}"

        else:
            pass

    except Exception as e:
        print(f"Poster fetch error: {e}")

    return FALLBACK_POSTER


def recommend(movie: str, movies: pd.DataFrame, similarity_matrix, api_key: str):
    """Core recommendation algorithm (UNCHANGED)"""
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity_matrix[movie_index]
    movies_list = sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for item in movies_list:
        movie_id = int(movies.iloc[item[0]].movie_id)
        recommended_movies.append(movies.iloc[item[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id, api_key))

    return recommended_movies, recommended_movies_posters


# ============================================================================
# PREMIUM THEME CSS
# ============================================================================
def apply_premium_theme():
    """Apply Cinematic dark theme with modern glassmorphism styling"""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,600;1,300&family=Inter:wght@300;400;600&display=swap');

        /* Main Background with film grain */
        .stApp {{
            background-color: {PREMIUM_COLORS['dark_bg']};
            background-image: 
                linear-gradient(rgba(3, 11, 20, 0.85), rgba(3, 11, 20, 0.92)),
                url('https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1920&q=20');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            filter: none;
            color: {PREMIUM_COLORS['text_primary']};
            font-family: 'Inter', sans-serif;
        }}

        .stApp::before {{
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            opacity: 0.08;
            pointer-events: none;
            z-index: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
            background-repeat: repeat;
            background-size: 128px 128px;
        }}
        
        h1, h2, h3, h4, h5, h6 {{ 
            font-family: 'Playfair Display', serif;
            color: {PREMIUM_COLORS['text_primary']}; 
            font-weight: 400;
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: {PREMIUM_COLORS['secondary_bg']};
            border-right: 1px solid rgba(212, 175, 55, 0.1);
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            color: {PREMIUM_COLORS['text_primary']};
        }}
        
        /* Main Content Area */
        [data-testid="stMainBlockContainer"] {{
        background-color: transparent;
        }}
        
        /* Text Elements */
        body {{ color: {PREMIUM_COLORS['text_primary']}; }}
        p {{ color: {PREMIUM_COLORS['text_secondary']}; }}
        
        /* Hero Section */
        .hero {{
            background: linear-gradient(135deg, rgba(3, 11, 20, 0.8), rgba(212, 175, 55, 0.05));
            border-radius: 16px;
            padding: 80px 32px;
            color: {PREMIUM_COLORS['text_primary']};
            margin-bottom: 32px;
            text-align: center;
        }}
        .hero h1 {{
            margin: 0;
            font-size: 4rem;
            font-weight: 700;
            letter-spacing: 2px;
            background: -webkit-linear-gradient(45deg, {PREMIUM_COLORS['primary_accent']}, #fdfdfd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .hero p {{
            margin-top: 16px;
            font-size: 1.4rem;
            font-style: italic;
            font-family: 'Playfair Display', serif;
            color: {PREMIUM_COLORS['text_secondary']};
        }}
        
        /* Mood Cards */
        .mood-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            justify-content: center;
            margin-bottom: 40px;
        }}
        .mood-card {{
            background: {PREMIUM_COLORS['card_bg']};
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 20px;
            padding: 20px 32px;
            font-size: 1.1rem;
            font-family: 'Playfair Display', serif;
            color: {PREMIUM_COLORS['primary_accent']};
            transition: all 0.4s ease;
            cursor: pointer;
            backdrop-filter: blur(8px);
        }}
        .mood-card:hover {{
            background: rgba(212, 175, 55, 0.1);
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(212, 175, 55, 0.15);
        }}

        /* Philosophy Section */
        .philosophy-section {{
            text-align: center;
            max-width: 800px;
            margin: 0 auto 40px auto;
            padding: 40px;
            border-top: 1px solid rgba(212, 175, 55, 0.2);
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        }}
        .philosophy-section p {{
            font-size: 1.25rem;
            line-height: 1.8;
            font-family: 'Playfair Display', serif;
            color: {PREMIUM_COLORS['text_secondary']};
        }}

        /* Movie Card */
        .movie-card {{
            background: {PREMIUM_COLORS['card_bg']};
            backdrop-filter: blur(8px);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.4s ease;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
            text-align: center;
        }}
        .movie-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 32px rgba(212, 175, 55, 0.2);
            border: 1px solid rgba(212, 175, 55, 0.4);
        }}
        .movie-title {{
            font-weight: 300;
            font-family: 'Playfair Display', serif;
            color: {PREMIUM_COLORS['text_primary']};
            padding: 12px 8px;
            font-size: 1rem;
            min-height: 56px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        /* Button Styling */
        .stButton > button {{
            background: transparent;
            color: {PREMIUM_COLORS['primary_accent']}; 
            border: 1px solid {PREMIUM_COLORS['primary_accent']}; 
            border-radius: 4px; 
            padding: 12px 40px;
            font-family: 'Inter', sans-serif;
            font-weight: 300; 
            font-size: 1.1rem; 
            transition: all 0.4s ease;
            letter-spacing: 1px;
        }}
        .stButton > button:hover {{
            background: rgba(212, 175, 55, 0.1);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(212, 175, 55, 0.2);
            color: #fff;
            border: 1px solid #fff;
        }}
        
        /* Select Box */
        .stSelectbox > div > div {{
            background: {PREMIUM_COLORS['card_bg']};
            border-color: rgba(212, 175, 55, 0.2);
            color: {PREMIUM_COLORS['text_primary']};
        }}

        /* Sidebar nav buttons */
        [data-testid="stSidebar"] .stButton > button {{
            background: transparent;
            border: none;
            color: #b0c4de;
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            letter-spacing: 2px;
            text-align: left;
            padding: 8px 0;
            border-radius: 0;
            border-left: 2px solid transparent;
            transition: all 0.3s ease;
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{
            color: #d4af37;
            border-left: 2px solid #d4af37;
            background: transparent;
            transform: none;
            box-shadow: none;
            padding-left: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )



# ============================================================================
# HELPER COMPONENTS
# ============================================================================
def render_philosophy():
    st.markdown(
    """
    <div class="philosophy-section">
        <p>People do not always choose movies based on genres.<br><br>
        They seek <span style="color: #d4af37;">a feeling</span> — comfort, wonder, escape,<br>reflection, or an emotional connection.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
    

# ============================================================================
# PAGE FUNCTIONS
# ============================================================================
def show_home(movies: pd.DataFrame, api_key: str):
    """Home page with hero, moods, philosophy, and call to action"""
    st.markdown(
    """
    <div class="hero" style="
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 900px; height: 500px;
            background: radial-gradient(ellipse at center, rgba(212,175,55,0.12) 0%, rgba(212,175,55,0.08) 40%, transparent 70%);
            pointer-events: none;
            z-index: 0;
        "></div>
        <div style="position: relative; z-index: 1;">
            <p style="letter-spacing: 4px; font-size: 0.85rem; color: #b0c4de; font-family: Inter, sans-serif; margin-bottom: 12px;">A CINEMATIC EXPERIENCE</p>
            <h1 style="font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 5rem; letter-spacing: 4px;">Musefall</h1>
            <p style="letter-spacing: 3px; font-size: 0.8rem; color: #b0c4de; font-family: Inter, sans-serif; margin: 8px 0 4px;">MOVIE RECOMMENDER</p>
            <div style="width: 200px; height: 1px; background: rgba(212,175,55,0.3); margin: 12px auto;"></div>
            <p>"Fall into the story you need."</p>
            <div style="display: flex; justify-content: center; gap: 60px; margin-top: 40px;">
                <div><div style="font-size: 2rem; color: #d4af37; font-family: Inter;">5,000+</div><div style="font-size: 0.65rem; letter-spacing: 2px; color: #b0c4de;">FILMS CATALOGUED</div></div>
                <div><div style="font-size: 2rem; color: #d4af37; font-family: Inter;">7</div><div style="font-size: 0.65rem; letter-spacing: 2px; color: #b0c4de;">MOODS EXPLORED</div></div>
                <div><div style="font-size: 2rem; color: #d4af37; font-family: Inter;">∞</div><div style="font-size: 0.65rem; letter-spacing: 2px; color: #b0c4de;">STORIES WAITING</div></div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

    st.markdown("<h3 style='text-align: center; margin-bottom: 24px; color: #d4af37; font-family: Playfair Display, serif;'>Explore by Mood</h3>", unsafe_allow_html=True)
    st.markdown(
    """
    <div class="mood-grid">
        <div class="mood-card">Wonder</div>
        <div class="mood-card">Curiosity</div>
        <div class="mood-card">Adrenaline</div>
        <div class="mood-card">Reflection</div>
        <div class="mood-card">Heartbreak</div>
        <div class="mood-card">Hope</div>
        <div class="mood-card">Mystery</div>
        <div class="mood-card">Nostalgia</div>
        <div class="mood-card">Rage</div>
        <div class="mood-card">Escape</div>
    </div>
    """,
    unsafe_allow_html=True
)

    render_philosophy()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            "<p style='color: #b0c4de; font-size: 0.95rem;'>Select a film that <span style='color: #d4af37;'>moved you</span> and we'll find your next cinematic chapter — curated by feeling, not just genre.</p>",
            unsafe_allow_html=True
    )
    with col2:
        if st.button("BEGIN YOUR JOURNEY ↗", use_container_width=True, type="primary"):
            st.session_state.current_page = "Discovery"
            st.rerun()

# Trending section — pick 6 random movies
    trending_sample = movies.sample(6)
    trending_html = '<div style="margin-bottom: 40px;"><h3 style="letter-spacing: 3px; font-size: 0.85rem; color: #d4af37; font-family: Inter;">CURRENTLY TRENDING</h3><div style="height: 1px; background: rgba(212,175,55,0.2); margin: 8px 0 16px;"></div><div style="display: flex; gap: 8px; overflow-x: auto;">'

    for _, row in trending_sample.iterrows():
        poster = fetch_poster(int(row["movie_id"]), api_key)
        trending_html += f'''
            <div style="min-width: 110px; border-radius: 6px; overflow: hidden; position: relative; cursor: pointer;">
                <img src="{poster}" style="width: 110px; height: 155px; object-fit: cover; display: block;" />
                <div style="position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(transparent, rgba(0,0,0,0.85)); padding: 20px 6px 6px; font-size: 0.7rem; color: #fff; font-family: Inter;">{row["title"]}</div>
            </div>'''

    trending_html += '</div></div>'
    st.markdown(trending_html, unsafe_allow_html=True)


def show_discovery(movies: pd.DataFrame, similarity, api_key: str):
    """Discovery page with movie selection and results"""
    st.markdown(
        """
        <div class="hero" style="padding: 40px 32px;">
            <h2>The Discovery Engine</h2>
            <p>Find the experience you are seeking.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not api_key:
        st.warning("⚠️ TMDB API key not found. Add TMDB_API_KEY in your .env file.")

    col1, col2 = st.columns([3, 1])

    with col1:
        selected_movie_name = st.selectbox(
            "What was the last story that moved you?",
            movies["title"].values,
            placeholder="Search for a film...",
        )

    with col2:
        st.write("")
        st.write("")
        recommend_button = st.button("Find My Story", type="primary", use_container_width=True)

    if recommend_button:
        try:
            with st.spinner("Weaving your cinematic journey..."):
                names, posters = recommend(selected_movie_name, movies, similarity, api_key)

            st.markdown("### ✨ Your Next Chapter")
            st.markdown("---")

            # Create responsive grid
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                with col:
                    st.image(posters[idx], use_container_width=True)
                    st.markdown(
                        f"<div class='movie-title'>{names[idx]}</div>",
                        unsafe_allow_html=True,
            )

        except Exception as ex:
            st.error(f"❌ Unable to generate recommendations: {ex}")

    st.markdown("---")


# ============================================================================
# MAIN APP
# ============================================================================
def main():
    # Page config
    st.set_page_config(
        page_title="Musefall",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Apply Premium theme
    apply_premium_theme()

    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
            <div style="padding: 24px 8px 16px; border-bottom: 1px solid rgba(212,175,55,0.2); margin-bottom: 24px;">
                <p style="font-family: 'Cormorant Garamond', serif; font-size: 1.6rem; font-weight: 700; color: #d4af37; margin: 0; letter-spacing: 2px;">Musefall</p>
                <p style="font-size: 0.6rem; letter-spacing: 3px; color: #b0c4de; margin: 4px 0 0;">CINEMATIC DISCOVERY</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size: 0.65rem; letter-spacing: 3px; color: #b0c4de; margin-bottom: 8px;'>NAVIGATE</p>", unsafe_allow_html=True)
        
        pages = ["Home", "Discovery"]
        for page in pages:
            is_active = st.session_state.current_page == page
            if st.button(
                page,
                key=f"nav_{page}",
                use_container_width=True,
            ):
                st.session_state.current_page = page
                st.rerun()

        st.markdown("<div style='height: 1px; background: rgba(212,175,55,0.15); margin: 24px 0;'></div>", unsafe_allow_html=True)

        st.markdown("<p style='font-size: 0.65rem; letter-spacing: 3px; color: #b0c4de; margin-bottom: 12px;'>FILTER</p>", unsafe_allow_html=True)

        st.markdown("<p style='font-size: 0.75rem; color: #d4af37; letter-spacing: 1px; margin-bottom: 4px;'>Genre</p>", unsafe_allow_html=True)
        genre_filter = st.selectbox("", ["All", "Action", "Adventure", "Comedy", "Drama", "Thriller", "Romance", "Science Fiction", "Horror", "Animation"], label_visibility="collapsed")

        st.markdown("<p style='font-size: 0.75rem; color: #d4af37; letter-spacing: 1px; margin: 12px 0 4px;'>Min Rating</p>", unsafe_allow_html=True)
        min_rating = st.slider("", 0.0, 10.0, 7.0, step=0.5, label_visibility="collapsed")

        st.markdown("<p style='font-size: 0.75rem; color: #d4af37; letter-spacing: 1px; margin: 12px 0 4px;'>Era</p>", unsafe_allow_html=True)
        era_filter = st.radio("", ["All Time", "Classic (pre-1990)", "90s–2000s", "Modern (2010+)"], label_visibility="collapsed")

        st.markdown("<div style='height: 1px; background: rgba(212,175,55,0.15); margin: 24px 0;'></div>", unsafe_allow_html=True)

        st.markdown("<p style='font-size: 0.65rem; letter-spacing: 3px; color: #b0c4de; margin-bottom: 8px;'>ABOUT</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.8rem; color: #b0c4de; line-height: 1.6;'>A cinematic journey curated by feeling, not just genre.</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.75rem; margin-top: 12px;'><a href='https://www.themoviedb.org/' style='color: #d4af37; text-decoration: none;'>TMDB</a> &nbsp;|&nbsp; <a href='https://github.com' style='color: #d4af37; text-decoration: none;'>GitHub</a></p>", unsafe_allow_html=True)

        st.session_state.genre_filter = genre_filter
        st.session_state.min_rating = min_rating
        st.session_state.era_filter = era_filter

    # Load data
    movies = load_movies()
    similarity = load_similarity()
    api_key = get_api_key()


    # Route to appropriate page
    if st.session_state.current_page == "Home":
        show_home(movies, api_key)
    elif st.session_state.current_page == "Discovery":
        show_discovery(movies, similarity, api_key)


if __name__ == "__main__":
    main()