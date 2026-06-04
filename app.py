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
    "dark_bg": "#060b19",          # Deep navy blue
    "card_bg": "rgba(20, 28, 47, 0.4)", # Glassmorphism base
    "secondary_bg": "#0a1128",     # Slightly lighter navy
    "primary_accent": "#00d2ff",   # Electric blue
    "accent_purple": "#7a00ff",    # Purple highlight
    "text_primary": "#ffffff",
    "text_secondary": "#a0aec0",
    "gold": "#ffd700",
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

        st.write(f"Movie ID: {movie_id}")
        st.write(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            poster_path = data.get("poster_path")
            st.write("Poster Path:", poster_path)

            if poster_path:
                return f"{TMDB_IMAGE_BASE_URL}{poster_path}"

        else:
            st.write(response.text)

    except Exception as e:
        st.error(f"Error: {e}")

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
        /* Main Background */
        .stApp {{
            background-color: {PREMIUM_COLORS['dark_bg']};
            color: {PREMIUM_COLORS['text_primary']};
        }}
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: {PREMIUM_COLORS['secondary_bg']};
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            color: {PREMIUM_COLORS['text_primary']};
        }}
        
        /* Main Content Area */
        [data-testid="stMainBlockContainer"] {{
            background-color: {PREMIUM_COLORS['dark_bg']};
        }}
        
        /* Text Elements */
        body {{ color: {PREMIUM_COLORS['text_primary']}; }}
        p {{ color: {PREMIUM_COLORS['text_secondary']}; }}
        h1, h2, h3, h4, h5, h6 {{ color: {PREMIUM_COLORS['text_primary']}; }}
        
        /* Hero Section */
        .hero {{
            background: linear-gradient(135deg, rgba(0, 210, 255, 0.1), rgba(122, 0, 255, 0.1));
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 56px 32px;
            color: {PREMIUM_COLORS['text_primary']};
            margin-bottom: 32px;
            border: 1px solid rgba(0, 210, 255, 0.2);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
            text-align: center;
        }}
        .hero h1 {{
            margin: 0;
            font-size: 3.5rem;
            font-weight: 800;
            background: -webkit-linear-gradient(45deg, {PREMIUM_COLORS['primary_accent']}, #ffffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .hero p {{
            margin-top: 16px;
            font-size: 1.3rem;
            color: {PREMIUM_COLORS['text_secondary']};
        }}
        
        /* Containers & Cards (Glassmorphism) */
        .featured-container, .how-it-works, .stat-card {{
            background: {PREMIUM_COLORS['card_bg']};
            backdrop-filter: blur(8px);
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 32px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }}
        .featured-container h2, .how-it-works h2 {{
            color: {PREMIUM_COLORS['primary_accent']};
            margin-bottom: 24px;
            font-size: 1.8rem;
        }}
        
        /* Stat Card specifics */
        .stat-card {{
            text-align: center;
            padding: 20px;
        }}
        .stat-card h3 {{
            margin: 0; font-size: 2rem; color: {PREMIUM_COLORS['primary_accent']};
        }}
        .stat-card p {{
            margin: 8px 0 0 0; color: {PREMIUM_COLORS['text_secondary']};
        }}
        
        /* Steps */
        .step {{
            display: flex; align-items: center; margin-bottom: 24px;
        }}
        .step-number {{
            background: linear-gradient(135deg, {PREMIUM_COLORS['primary_accent']}, {PREMIUM_COLORS['accent_purple']});
            color: white; width: 50px; height: 50px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: 900; font-size: 1.5rem; margin-right: 20px; flex-shrink: 0;
        }}
        .step-content h3 {{ margin: 0 0 8px 0; }}
        .step-content p {{ margin: 0; }}
        
        /* Movie Card */
        .movie-card {{
            background: {PREMIUM_COLORS['card_bg']};
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            text-align: center;
        }}
        .movie-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 32px rgba(0, 210, 255, 0.2);
            border: 1px solid rgba(0, 210, 255, 0.5);
        }}
        .movie-card img {{
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .movie-title {{
            font-weight: 600;
            color: {PREMIUM_COLORS['text_primary']};
            padding: 12px 8px;
            font-size: 0.95rem;
            min-height: 56px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        /* Button Styling */
        .stButton > button {{
            background: linear-gradient(135deg, {PREMIUM_COLORS['primary_accent']}, {PREMIUM_COLORS['accent_purple']});
            color: white; border: none; border-radius: 8px; padding: 12px 32px;
            font-weight: 700; font-size: 1.1rem; transition: all 0.3s ease;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 210, 255, 0.4);
        }}
        
        /* Select Box */
        .stSelectbox > div > div {{
            background: {PREMIUM_COLORS['card_bg']};
            border-color: rgba(255, 255, 255, 0.1);
            color: {PREMIUM_COLORS['text_primary']};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )



# ============================================================================
# HELPER COMPONENTS
# ============================================================================
def render_featured_movie(movies: pd.DataFrame, api_key: str):
    """Render featured movie section"""
    featured = movies.sample(n=1).iloc[0]
    movie_id = int(featured.movie_id)
    poster = fetch_poster(movie_id, api_key)

    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.image(poster, use_container_width=True)

    with col2:
        st.markdown(f"### 🌟 Featured Movie")
        st.markdown(f"## {featured.title}")
        st.markdown(
            f"**Genres:** {featured.get('genres', 'N/A')} | **Rating:** ⭐ {featured.get('vote_average', 'N/A')}/10"
        )


def render_how_it_works():
    """Render how it works section"""
    st.markdown(
        """
        <div class="how-it-works">
            <h2>🎬 How It Works</h2>
            <div class="step">
                <div class="step-number">1</div>
                <div class="step-content">
                    <h3>Choose Your Favorite</h3>
                    <p>Select any movie from our database of thousands of titles.</p>
                </div>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <div class="step-content">
                    <h3>AI Analysis</h3>
                    <p>Our advanced ML algorithm analyzes movie features and similarities.</p>
                </div>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <div class="step-content">
                    <h3>Get Recommendations</h3>
                    <p>Discover 5 perfectly matched movies tailored to your taste.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# PAGE FUNCTIONS
# ============================================================================
def show_home(movies: pd.DataFrame, api_key: str):
    """Home page with featured movie and call to action"""
    st.markdown(
        """
        <div class="hero">
            <h1>🎬 Movie Recommender</h1>
            <p>Discover your next favorite movie with AI-powered recommendations</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button("🚀 Start Exploring", use_container_width=True, type="primary"):
            st.session_state.current_page = "Recommender"
            st.rerun()

    st.write("")
    #st.markdown("### 🔥 Trending Now")
    # cols = st.columns(5)
    # trending_movies = movies.sample(n=5)
    # for idx, col in enumerate(cols):
    #     movie_row = trending_movies.iloc[idx]
    #     poster = fetch_poster(int(movie_row.movie_id), api_key)
    #     with col:
    #         st.markdown(
    #             f'''
    #             <div class="movie-card" style="margin-bottom: 24px;">
    #                 <img src="{poster}" style="width:100%; display:block;">
    #                 <div class='movie-title'>{movie_row.title}</div>
    #             </div>
    #             ''',
    #             unsafe_allow_html=True,
    #         )

   # render_featured_movie(movies, api_key)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-card"><h3>{len(movies):,}</h3><p>Movies available</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card"><h3>⚡</h3><p>Instant recommendations</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-card"><h3>🧠</h3><p>Content-based filtering</p></div>', unsafe_allow_html=True)

    render_how_it_works()


def show_recommender(movies: pd.DataFrame, similarity, api_key: str):
    """Recommender page with movie selection and results"""
    st.markdown(
        """
        <div class="hero">
            <h1>🎯 Find Your Next Favorite</h1>
            <p>Choose a movie you love, get 5 perfect recommendations</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not api_key:
        st.warning("⚠️ TMDB API key not found. Add TMDB_API_KEY in your .env file.")

    col1, col2 = st.columns([3, 1])

    with col1:
        selected_movie_name = st.selectbox(
            "🎬 Search movies...",
            movies["title"].values,
            placeholder="Type to search...",
        )

    with col2:
        st.write("")
        st.write("")
        recommend_button = st.button("Get Recommendations", type="primary", use_container_width=True)

    if recommend_button:
        try:
            with st.spinner("🎬 Finding perfect matches for you..."):
                names, posters = recommend(selected_movie_name, movies, similarity, api_key)

            st.markdown("### ✨ Recommended For You")
            st.markdown(f"*Based on: **{selected_movie_name}***")
            st.markdown("---")

            # Create responsive grid
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                with col:
                    st.markdown(
                        f'''
                        <div class="movie-card">
                            <img src="{posters[idx]}" style="width:100%; display:block;">
                            <div class='movie-title'>{names[idx]}</div>
                        </div>
                        ''',
                        unsafe_allow_html=True,
                    )

            st.success("🎉 Recommendations loaded! Enjoy!!")

        except Exception as ex:
            st.error(f"❌ Unable to generate recommendations: {ex}")

    st.markdown("---")
    with st.expander("💡 How to get better recommendations"):
        st.markdown(
            """
            - **Pick a movie you loved:** The more specific and accurate your selection, the better the recommendations
            - **Fine-tune:** Come back and try different movies to explore more recommendations
            """
        )


# ============================================================================
# MAIN APP
# ============================================================================
def main():
    # Page config
    st.set_page_config(
        page_title="Movie Recommender",
        page_icon="🎬",
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
        st.markdown("### 🎬 Navigation")
        pages = ["Home", "Recommender"]
        selected = st.radio(
            "Choose a page:",
            pages,
            index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0,
        )
        st.session_state.current_page = selected

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("A cinematic movie recommendation system powered by machine learning.")
        st.markdown("### 🔗 Links")
        st.markdown("[TMDB](https://www.themoviedb.org/)  |  [GitHub](https://github.com)")

    # Load data
    movies = load_movies()
    similarity = load_similarity()
    api_key = get_api_key()


    # Route to appropriate page
    if st.session_state.current_page == "Home":
        show_home(movies, api_key)
    elif st.session_state.current_page == "Recommender":
        show_recommender(movies, similarity, api_key)


if __name__ == "__main__":
    main()