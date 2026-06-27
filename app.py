import os
import pickle
from pathlib import Path
import gdown
import random

import pandas as pd
import requests
import streamlit as st
import json as _json
import streamlit.components.v1 as components

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
def load_movies_full() -> pd.DataFrame:
    return pd.read_csv("tmdb_5000_movies.csv")


@st.cache_data(show_spinner=False)
def load_movies() -> pd.DataFrame:
    with open("movie_with_moods.pkl", "rb") as f:
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
        
        .disc-hero {{
            position: relative;
            padding: 40px 48px 28px;
            overflow: hidden;
        }}
        .disc-glow {{
            position: absolute;
            top: -40px; right: 60px;
            width: 320px; height: 220px;
            background: radial-gradient(ellipse, rgba(212,175,55,0.08) 0%, transparent 70%);
            pointer-events: none;
        }}
        .disc-eyebrow {{
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 4px;
            text-transform: uppercase;
            color: rgba(212,175,55,0.6);
            margin: 0 0 10px;
            position: relative;
        }}
        .disc-hero .disc-title {{
            font-family: 'Cormorant Garamond', serif !important;
            font-weight: 600 !important;
            font-size: 2.6rem;
            color: #f0d98c !important;
            line-height: 1.1;
            margin: 0 0 12px;
            position: relative;
        }}
        .disc-sub {{
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: 1rem;
            color: #8a9aa8;
            margin: 0;
            position: relative;
        }}
 
        .disc-search-wrap {{
            padding: 8px 48px 4px;
        }}
        .disc-search-label {{
            font-size: 15px;
            font-weight: 600;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: rgba(212,175,55,0.6);
            margin: 0 0 12px;
            display: block;
        }}
 
        /* align selectbox + button in the same row, same height */
        .disc-search-wrap [data-testid="stHorizontalBlock"] {{
            align-items: stretch;
            gap: 12px;
        }}
        .disc-search-wrap .stSelectbox {{
            height: 100%;
        }}
        .disc-search-wrap .stSelectbox > div > div {{
            background: #0a1620;
            border: 1px solid rgba(212,175,55,0.25);
            border-radius: 6px;
            min-height: 46px;
            display: flex;
            align-items: center;
            color: #cdd8e0;
        }}
        .disc-search-wrap .stButton {{
            height: 100%;
            display: flex;
            align-items: stretch;
        }}
        .disc-search-wrap .stButton > button {{
            width: 100%;
            height: 46px;
            border: 1px solid #d4af37;
            background: rgba(212,175,55,0.08);
            color: #f0d060;
            font-size: 0.8rem;
            letter-spacing: 2px;
            border-radius: 6px;
        }}
 
        .recent-row {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 16px 48px 8px;
            flex-wrap: wrap;
        }}
        .recent-label {{
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: rgba(212,175,55,0.45);
        }}
        .recent-chip {{
            font-size: 0.75rem;
            color: #d4af37;
            border: 1px solid rgba(212,175,55,0.3);
            border-radius: 20px;
            padding: 4px 14px;
            cursor: pointer;
            transition: all 0.2s;
            background: transparent;
        }}
        .recent-chip:hover {{
            background: rgba(212,175,55,0.08);
            border-color: #d4af37;
        }}
 
        .results-header {{
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 28px 48px 18px;
        }}
        .results-label {{
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: rgba(212,175,55,0.55);
            white-space: nowrap;
        }}
        .results-rule {{
            flex: 1;
            height: 1px;
            background: rgba(212,175,55,0.12);
        }}
        .results-count {{
            font-size: 10px;
            letter-spacing: 2px;
            color: rgba(212,175,55,0.4);
        }}
 
        /* results grid uses Streamlit columns; this styles the column content */
        .rec-poster {{
            aspect-ratio: 2/3;
            border-radius: 8px;
            border: 1px solid rgba(212,175,55,0.15);
            overflow: hidden;
            margin-bottom: 10px;
            position: relative;
            transition: border-color 0.3s, box-shadow 0.3s;
        }}
        .rec-poster:hover {{
            border-color: rgba(212,175,55,0.4);
            box-shadow: 0 10px 28px rgba(0,0,0,0.55);
            transform: translateY(-4px);
        }}
        .rec-poster img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}
        .rec-bookmark {{
            position: absolute;
            top: 8px; right: 8px;
            width: 26px; height: 26px;
            border-radius: 50%;
            background: rgba(4,12,22,0.8);
            border: 1px solid rgba(212,175,55,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            color: #d4af37;
        }}
        .rec-title {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 0.85rem;
            color: #cdd8e0;
            text-align: center;
            line-height: 1.35;
            margin-bottom: 6px;
            min-height: 34px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .rec-score {{
            font-size: 0.65rem;
            letter-spacing: 1px;
            color: #d4af37;
            border: 1px solid rgba(212,175,55,0.3);
            border-radius: 10px;
            padding: 2px 8px;
            display: block;
            text-align: center;
            width: fit-content;
            margin: 0 auto 8px;
        }}
 
        /* Save buttons — full width of their column, matches poster width */
        .rec-col .stButton > button {{
            width: 100%;
            font-size: 0.7rem;
            letter-spacing: 1px;
            padding: 8px 0;
            border: 1px solid rgba(212,175,55,0.3);
            background: transparent;
            color: rgba(212,175,55,0.8);
            border-radius: 5px;
        }}
        .rec-col .stButton > button:hover {{
            border-color: #d4af37;
            color: #f0d060;
            background: rgba(212,175,55,0.06);
        }}
 
        .disc-empty {{
            padding: 56px 48px 60px;
            text-align: center;
        }}
        .disc-empty-icon {{
            font-size: 2rem;
            color: rgba(212,175,55,0.25);
            margin-bottom: 16px;
        }}
        .disc-empty-title {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.2rem;
            font-style: italic;
            color: #6a7a88;
            margin-bottom: 8px;
        }}
        .disc-empty-hint {{
            font-size: 0.72rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: rgba(212,175,55,0.3);
        }}

        @keyframes mfFadeIn {{
            from {{opacity: 0; transform: translateY(8px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        [data-testid="stMainBlockContainer"] > div:first-child {{
            animation: mfFadeIn 0.45s ease-out;
        }}
 
        .page-bg-dark {{
            background-color: #060e1a;
            padding: 0;
            min-height: 100vh;
        }}
    
        /* Sidebar nav links styled like tabs */
        .nav-link {{
            display: block;
            text-decoration: none;
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            letter-spacing: 2px;
            color: #5a7080;
            padding: 8px 0 8px 10px;
            border-left: 2px solid transparent;
            transition: all 0.25s ease;
            margin-bottom: 2px;
        }}
        .nav-link:hover {{
            color: #d4af37;
            border-left-color: rgba(212,175,55,0.4);
            padding-left: 14px;
        }}
        .nav-link.active {{
            color: #d4af37;
            border-left-color: #d4af37;
            padding-left: 14px;
        }}

        /* Dark bg for non-home pages — targets main content area */
        [data-testid="stMainBlockContainer"] {{
            background-color: #060e1a !important;
        }}

        /*explore page specific styles */
        .exp-hero {{
            position: relative;
            padding: 40px 48px 28px;
        }}
        .exp-eyebrow {{
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 4px;
            text-transform: uppercase;
            color: rgba(212,175,55,0.6);
            margin: 0 0 10px;
            display: block;
        }}
        .exp-hero .exp-title {{
            font-family: 'Cormorant Garamond', serif !important;
            font-weight: 600 !important;
            font-size: 2.6rem;
            color: #f0d98c !important;
            line-height: 1.1;
            margin: 0 0 12px;
        }}
        .exp-sub {{
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: 1rem;
            color: #8a9aa8;
            margin: 0;
        }}
 
        .exp-filter-section {{
            padding: 8px 48px 4px;
        }}
        .exp-filter-label {{
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: rgba(212,175,55,0.5);
            margin: 16px 0 10px;
            display: block;
        }}
 
        /* Explore pill buttons — nowrap is critical */
        .exp-filter-section div[data-testid="stColumn"] {{
            padding: 0 4px !important;
            flex: 0 0 auto !important;
            width: auto !important;
            min-width: unset !important;
        }}
        .exp-filter-section div[data-testid="stColumn"] .stButton > button {{
            white-space: nowrap !important;
            width: auto !important;
            min-width: unset !important;
            padding: 6px 14px !important;
            border-radius: 30px !important;
            border: 1px solid rgba(212,175,55,0.3) !important;
            background: transparent !important;
            color: #d4af37 !important;
            font-size: 0.78rem !important;
            letter-spacing: 1px !important;
            height: 34px !important;
            line-height: 1 !important;
            font-weight: 300 !important;
        }}
        .exp-filter-section div[data-testid="stColumn"] .stButton > button:hover {{
            background: rgba(212,175,55,0.08) !important;
            border-color: #d4af37 !important;
            color: #f0d060 !important;
            transform: none !important;
            box-shadow: none !important;
        }}
 
        .exp-sort-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 48px;
            border-top: 1px solid rgba(212,175,55,0.07);
            border-bottom: 1px solid rgba(212,175,55,0.07);
            margin-top: 16px;
        }}
        .exp-count {{
            font-size: 10px;
            letter-spacing: 2px;
            color: rgba(212,175,55,0.4);
        }}
 
        .exp-grid-wrap {{
            padding: 24px 48px 40px;
        }}
        .exp-poster {{
            aspect-ratio: 2/3;
            border-radius: 8px;
            border: 1px solid rgba(212,175,55,0.15);
            overflow: hidden;
            margin-bottom: 8px;
            position: relative;
            transition: border-color 0.3s, box-shadow 0.3s, transform 0.3s;
        }}
        .exp-poster:hover {{
            border-color: rgba(212,175,55,0.4);
            box-shadow: 0 10px 28px rgba(0,0,0,0.55);
            transform: translateY(-4px);
        }}
        .exp-poster img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}
        .exp-rating {{
            position: absolute;
            top: 8px; left: 8px;
            background: rgba(4,12,22,0.85);
            border: 1px solid rgba(212,175,55,0.3);
            border-radius: 5px;
            padding: 2px 7px;
            font-size: 0.65rem;
            color: #d4af37;
        }}
        .exp-rtitle {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 0.82rem;
            color: #cdd8e0;
            text-align: center;
            line-height: 1.35;
            min-height: 34px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
 
        .exp-empty {{
            padding: 56px 48px 60px;
            text-align: center;
        }}
        .exp-empty-icon {{
            font-size: 2rem;
            color: rgba(212,175,55,0.25);
            margin-bottom: 16px;
        }}
        .exp-empty-title {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.2rem;
            font-style: italic;
            color: #6a7a88;
        }}

        /* watchlist page specific styles */
        .wl-hero {{
            position: relative;
            padding: 40px 48px 28px;
        }}
        .wl-eyebrow {{
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 4px;
            text-transform: uppercase;
            color: rgba(212,175,55,0.6);
            margin: 0 0 10px;
        }}
        .wl-hero .wl-title {{
            font-family: 'Cormorant Garamond', serif !important;
            font-weight: 600 !important;
            font-size: 2.6rem;
            color: #f0d98c !important;
            line-height: 1.1;
            margin: 0 0 12px;
        }}
        .wl-sub {{
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: 1rem;
            color: #8a9aa8;
            margin: 0;
        }}
        .wl-stats-row {{
            display: flex;
            align-items: center;
            gap: 32px;
            padding: 16px 48px;
            border-top: 1px solid rgba(212,175,55,0.07);
            border-bottom: 1px solid rgba(212,175,55,0.07);
            margin-bottom: 8px;
        }}
        .wl-stat {{
            text-align: center;
        }}
        .wl-stat-num {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.6rem;
            color: #d4af37;
            line-height: 1;
        }}
        .wl-stat-lbl {{
            font-size: 9px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #3a5060;
            margin-top: 3px;
        }}
        .wl-grid-wrap {{
            padding: 20px 48px 40px;
        }}
        .wl-poster {{
            aspect-ratio: 2/3;
            border-radius: 8px;
            border: 1px solid rgba(212,175,55,0.15);
            overflow: hidden;
            margin-bottom: 8px;
            position: relative;
            transition: border-color 0.3s, box-shadow 0.3s, transform 0.3s;
        }}
        .wl-poster:hover {{
            border-color: rgba(212,175,55,0.4);
            box-shadow: 0 10px 28px rgba(0,0,0,0.55);
            transform: translateY(-4px);
        }}
        .wl-poster img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}
        .wl-rating {{
            position: absolute;
            top: 8px; left: 8px;
            background: rgba(4,12,22,0.85);
            border: 1px solid rgba(212,175,55,0.3);
            border-radius: 5px;
            padding: 2px 7px;
            font-size: 0.65rem;
            color: #d4af37;
        }}
        .wl-title-text {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 0.82rem;
            color: #cdd8e0;
            text-align: center;
            line-height: 1.35;
            min-height: 34px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 6px;
        }}
        .wl-empty {{
            padding: 80px 48px;
            text-align: center;
        }}
        .wl-empty-icon {{
            font-size: 2.5rem;
            color: rgba(212,175,55,0.15);
            margin-bottom: 20px;
        }}
        .wl-empty-title {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.4rem;
            font-style: italic;
            color: #4a6070;
            margin-bottom: 10px;
        }}
        .wl-empty-hint {{
            font-size: 0.72rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: rgba(212,175,55,0.25);
            margin-bottom: 32px;
        }}
        /* remove button styling */
        .wl-grid-wrap div[data-testid="stColumn"] .stButton > button {{
            width: 100% !important;
            font-size: 0.68rem !important;
            letter-spacing: 1px !important;
            padding: 6px 0 !important;
            border: 1px solid rgba(212,175,55,0.2) !important;
            background: transparent !important;
            color: rgba(212,175,55,0.5) !important;
            border-radius: 5px !important;
            font-weight: 300 !important;
        }}
        .wl-grid-wrap div[data-testid="stColumn"] .stButton > button:hover {{
            border-color: rgba(220,60,60,0.5) !important;
            color: rgba(220,100,100,0.9) !important;
            background: rgba(220,60,60,0.06) !important;
            transform: none !important;
            box-shadow: none !important;
        }}

        /* Watchlist note input */
        .wl-grid-wrap .stTextInput > div > div > input {{
            background: transparent !important;
            border: none !important;
            border-bottom: 1px solid rgba(212,175,55,0.15) !important;
            border-radius: 0 !important;
            color: #6a7a88 !important;
            font-size: 0.7rem !important;
            font-style: italic !important;
            padding: 4px 0 !important;
            text-align: center !important;
        }}
        .wl-grid-wrap .stTextInput > div > div > input:focus {{
            border-bottom-color: rgba(212,175,55,0.4) !important;
            box-shadow: none !important;
        }}

        /* Film detail buttons */
        .fd-back-btn > button {{
            background: transparent !important;
            border: none !important;
            color: rgba(212,175,55,0.5) !important;
            font-size: 0.72rem !important;
            letter-spacing: 2px !important;
            padding: 0 !important;
            font-weight: 300 !important;
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
    st.markdown("""
    <style>
    .stApp { background-image: linear-gradient(rgba(3,11,20,0.85), rgba(3,11,20,0.92)), url('https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1920&q=20') !important; }
    [data-testid="stMainBlockContainer"] { background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)
    
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
        <div class="mood-card">Sorrow</div>
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
            st.session_state.current_page = "Recommend"
            st.rerun()

    #Trending section — pick 6 random movies
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


def show_recommend(movies, similarity, api_key):
 
    if "recent_searches" not in st.session_state:
        st.session_state.recent_searches = []
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = []
 
    st.markdown("""
    <style>
        .stApp { background-image: none !important; background-color: #060e1a !important; }
        .stApp::before { display: none !important; }
        [data-testid="stMainBlockContainer"] { background-color: #060e1a !important; }
        </style>
        """, unsafe_allow_html=True)

    # Hero
    st.markdown("""
    <div class="disc-hero">
        <div class="disc-glow"></div>
        <div class="disc-eyebrow">The Recommendation Engine</div>
        <div class="disc-title">Find Your<br>Next Chapter</div>
        <p class="disc-sub">"Find the experience you are seeking."</p>
    </div>
    """, unsafe_allow_html=True)
 
    if not api_key:
        st.warning("⚠️ TMDB API key not found. Add TMDB_API_KEY to your .env file.")
 
    # Search row
    st.markdown("""
    <div class="disc-search-wrap">
        <span class="disc-search-label">What was the last story that moved you?</span>
    </div>
    """, unsafe_allow_html=True)
 
    st.markdown('<div class="disc-search-wrap">', unsafe_allow_html=True)
    default_movie = st.session_state.pop("recent_clicked", None)
    col_select, col_btn = st.columns([3, 1])
    with col_select:
        movie_list = movies["title"].values.tolist()
        default_idx = movie_list.index(default_movie) if default_movie and default_movie in movie_list else 0
        selected_movie = st.selectbox(
            label="",
            options=movie_list,
            index=default_idx,
            placeholder="Search for a film...",
            label_visibility="collapsed",
            key="disc_select",
        )
    with col_btn:
        find_btn = st.button("Find My Story", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
 
    # Recent searches — real buttons styled as chips
    if st.session_state.recent_searches:
        st.markdown('<div class="recent-row"><span class="recent-label">Your searches</span></div>', unsafe_allow_html=True)
        chip_cols = st.columns(len(st.session_state.recent_searches[-4:]) + 4)
        for i, title in enumerate(st.session_state.recent_searches[-4:]):
            with chip_cols[i]:
                if st.button(title, key=f"recent_{i}_{title}"):
                    st.session_state["recent_clicked"] = title
                    st.rerun()
 
    # Results
    if find_btn and selected_movie:
        recent = st.session_state.recent_searches
        if selected_movie in recent:
            recent.remove(selected_movie)
        recent.append(selected_movie)
        st.session_state.recent_searches = recent[-4:]
 
        with st.spinner("Weaving your cinematic journey..."):
            try:
                names, posters = recommend(selected_movie, movies, similarity, api_key)
                st.session_state.last_names = names
                st.session_state.last_posters = posters
            except Exception as ex:
                st.error(f"❌ Could not generate recommendations: {ex}")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()

    if "last_names" in st.session_state and "last_posters" in st.session_state:
        names = st.session_state.last_names
        posters = st.session_state.last_posters
    
        st.markdown("""
        <div class="results-header">
            <span class="results-label">Your next chapter</span>
            <div class="results-rule"></div>
            <span class="results-count">5 films</span>
        </div>
        """, unsafe_allow_html=True)
 
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.markdown('<div class="rec-col">', unsafe_allow_html=True)
 
                in_wl = names[i] in st.session_state.watchlist
                bookmark = "★" if in_wl else "☆"
 
                st.markdown(f"""
                <div class="rec-poster">
                    <img src="{posters[i]}" alt="{names[i]}" loading="lazy" />
                    <div class="rec-bookmark">{bookmark}</div>
                </div>
                <div class="rec-title">{names[i]}</div>
                <div class="rec-score">✦ match</div>
                """, unsafe_allow_html=True)
 
                label = "★ Saved" if in_wl else "☆ Save"
                if st.button(label, key=f"wl_{i}_{names[i]}", use_container_width=True):
                    if in_wl:
                        st.session_state.watchlist.remove(names[i])
                    else:
                        st.session_state.watchlist.append(names[i])
                    st.rerun()
                if st.button("View Details", key=f"fd_{i}_{names[i]}", use_container_width=True):
                    st.session_state.selected_film = names[i]
                    st.session_state.film_detail_source = "Recommend"
                    st.session_state.current_page = "FilmDetail"
                    st.rerun()
 
                st.markdown('</div>', unsafe_allow_html=True)
 
    else:
        st.markdown("""
        <div class="disc-empty">
            <div class="disc-empty-icon">✦</div>
            <div class="disc-empty-title">Select a film above to begin your journey.</div>
            <div class="disc-empty-hint">5 recommendations await</div>
        </div>
        """, unsafe_allow_html=True)


 
MOOD_OPTIONS = [
    "Wonder", "Curiosity", "Adrenaline", "Reflection",
    "Sorrow", "Hope", "Mystery", "Nostalgia",
]
 
GENRE_OPTIONS = [
    "All", "Action", "Adventure", "Comedy", "Drama",
    "Thriller", "Romance", "Science Fiction", "Horror", "Animation",
]
 
ERA_OPTIONS = ["All Time", "Classic (pre-1990)", "90s–2000s", "Modern (2010+)"]
 
SORT_OPTIONS = ["Top Rated", "Newest", "Most Popular"]
 
 
def _parse_genres(genres_json):
    try:
        items = _json.loads(genres_json) if isinstance(genres_json, str) else genres_json
        return [g["name"] for g in items]
    except Exception:
        return []
 
 
def show_explore(movies_full, movies, api_key):
    if "explore_mood" not in st.session_state:
        st.session_state.explore_mood = None  # visual-only selection for now
    if "explore_genre" not in st.session_state:
        st.session_state.explore_genre = "All"
    if "explore_sort" not in st.session_state:
        st.session_state.explore_sort = "Top Rated"  

    filtered = movies_full.copy()
 
    if st.session_state.explore_genre != "All":
        filtered = filtered[
            filtered["genres"].apply(lambda g: st.session_state.explore_genre in _parse_genres(g))
        ]
  
 
    st.markdown("""
    <style>
    .stApp { background-image: none !important; background-color: #060e1a !important; }
    .stApp::before { display: none !important; }
    [data-testid="stMainBlockContainer"] { background-color: #060e1a !important; }
    </style>
    """, unsafe_allow_html=True)
 
    # Hero
    st.markdown("""
    <div class="exp-hero">
        <div class="exp-eyebrow">Browse the collection</div>
        <div class="exp-title">Explore Every<br>Story</div>
        <p class="exp-sub">"Wander until something finds you."</p>
    </div>
    """, unsafe_allow_html=True)
 
   # ── Mood filter ──
    st.markdown('<span class="exp-filter-label">Mood</span>', unsafe_allow_html=True)
    mood_row = st.columns(8)
    for i, mood in enumerate(MOOD_OPTIONS):
        with mood_row[i]:
            is_active = st.session_state.explore_mood == mood
            label = f"✦ {mood}" if is_active else mood
            if st.button(label, key=f"mood_{mood}", use_container_width=True):
                st.session_state.explore_mood = None if is_active else mood
                st.rerun()

    # ── Genre filter ──
    st.markdown('<span class="exp-filter-label">Genre</span>', unsafe_allow_html=True)
    genre_row1 = st.columns(5)
    genre_row2 = st.columns(5)
    for i, genre in enumerate(GENRE_OPTIONS):
        row = genre_row1 if i < 5 else genre_row2
        with row[i % 5]:
            is_active = st.session_state.explore_genre == genre
            label = f"✦ {genre}" if is_active else genre
            if st.button(label, key=f"genre_{genre}", use_container_width=True):
                st.session_state.explore_genre = genre
                st.rerun()
    
    # Rating filter from sidebar
    min_rating = st.session_state.get('min_rating', 0)
    filtered = filtered[filtered['vote_average'] >= min_rating]

    # Era filter
    era = st.session_state.get('era_filter', 'All Time')
    if era == 'Classic (pre-1990)':
        filtered = filtered[filtered['release_date'] < '1990']
    elif era == '90s–2000s':
        filtered = filtered[(filtered['release_date'] >= '1990') & (filtered['release_date'] < '2010')]
    elif era == 'Modern (2010+)':
        filtered = filtered[filtered['release_date'] >= '2010']

    if st.session_state.explore_mood:
        mood_col = f"mood_{st.session_state.explore_mood.lower()}"
        if mood_col in movies.columns:
            mood_scores = movies[["movie_id", mood_col]].copy()
            mood_scores = mood_scores.rename(columns={"movie_id": "id"})
            filtered = filtered.merge(mood_scores, on="id", how="left")
            filtered = filtered[filtered[mood_col] > 0]
            filtered = filtered.sort_values(mood_col, ascending=False)
        else:
            filtered = filtered.sort_values("vote_average", ascending=False)
    else:
        sort_map = {
            "Top Rated": ("vote_average", False),
            "Newest": ("release_date", False),
            "Most Popular": ("popularity", False),
        }
        sort_col, asc = sort_map[st.session_state.explore_sort]
        filtered = filtered.sort_values(sort_col, ascending=asc)

    # ── Sort ──
    st.markdown(f'<div class="exp-sort-row"><span class="exp-count">{len(filtered)} films match</span></div>', unsafe_allow_html=True)
    sort_row = st.columns([1, 1, 1, 4])
    for i, sort_opt in enumerate(SORT_OPTIONS):
        with sort_row[i]:
            is_active = st.session_state.explore_sort == sort_opt
            label = f"✦ {sort_opt}" if is_active else sort_opt
            if st.button(label, key=f"sort_{sort_opt}", use_container_width=True):
                st.session_state.explore_sort = sort_opt
                st.rerun()
 
    # ── Grid ─────────────────────────────────────────────────────────────
    top_results = filtered.head(20)
 
    if top_results.empty:
        st.markdown("""
        <div class="exp-empty">
            <div class="exp-empty-icon">✦</div>
            <div class="exp-empty-title">No films match these filters yet.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="exp-grid-wrap">', unsafe_allow_html=True)
        rows = [top_results.iloc[i:i+4] for i in range(0, len(top_results), 4)]
        for row in rows:
            cols = st.columns(4)
            for col, (_, movie) in zip(cols, row.iterrows()):
                with col:
                    poster = fetch_poster(int(movie["id"]), api_key)
                    rating = movie.get("vote_average", 0)
                    st.markdown(f"""
                    <div class="exp-poster">
                        <img src="{poster}" alt="{movie['title']}" loading="lazy" />
                        <div class="exp-rating">★ {rating:.1f}</div>
                    </div>
                    <div class="exp-rtitle">{movie['title']}</div>
                    """, unsafe_allow_html=True)
                    if st.button("View", key=f"exp_view_{movie['id']}", use_container_width=True):
                        st.session_state.selected_film = movie["title"]
                        st.session_state.film_detail_source = "Explore"
                        st.session_state.current_page = "FilmDetail"
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def show_watchlist(movies_full, api_key):

    if "watchlist" not in st.session_state:
        st.session_state.watchlist = []
    if "wl_notes" not in st.session_state:
        st.session_state.wl_notes = {}

    st.markdown("""
    <style>
    .stApp { background-image: none !important; background-color: #060e1a !important; }
    .stApp::before { display: none !important; }
    [data-testid="stMainBlockContainer"] { background-color: #060e1a !important; }
    </style>
    """, unsafe_allow_html=True)

    count = len(st.session_state.watchlist)
    notes_count = sum(1 for n in st.session_state.wl_notes.values() if n.strip())

    # Hero
    st.markdown(f"""
    <div class="wl-hero">
        <div class="wl-eyebrow">Your Collection</div>
        <div class="wl-title">My Watchlist</div>
        <p class="wl-sub">"Films worth your time."</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats bar
    st.markdown(f"""
    <div class="wl-stats-row">
        <div class="wl-stat">
            <div class="wl-stat-num">{count}</div>
            <div class="wl-stat-lbl">FILMS SAVED</div>
        </div>
        <div class="wl-stat">
            <div class="wl-stat-num">{notes_count}</div>
            <div class="wl-stat-lbl">NOTES WRITTEN</div>
        </div>
        <div class="wl-stat">
            <div class="wl-stat-num" style="font-size: 1rem; padding-top: 4px;">{"Recommend · Explore" if count > 0 else "—"}</div>
            <div class="wl-stat-lbl">SOURCES</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs row
    st.markdown("""
    <div style="display: flex; gap: 0; padding: 0 48px; border-bottom: 1px solid rgba(212,175,55,0.08); margin-bottom: 8px;">
        <div style="font-size: 0.72rem; letter-spacing: 2px; color: #d4af37; padding: 12px 0; margin-right: 32px; border-bottom: 2px solid #d4af37;">ALL FILMS</div>
        <div style="font-size: 0.72rem; letter-spacing: 2px; color: rgba(212,175,55,0.3); padding: 12px 0; margin-right: 32px; border-bottom: 2px solid transparent;">WATCHED</div>
        <div style="font-size: 0.72rem; letter-spacing: 2px; color: rgba(212,175,55,0.3); padding: 12px 0; border-bottom: 2px solid transparent;">UNWATCHED</div>
    </div>
    """, unsafe_allow_html=True)

    # Sort row
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 48px 0;">
        <span style="font-size: 10px; letter-spacing: 2px; color: rgba(212,175,55,0.35);">SORT BY</span>
        <div style="display: flex; gap: 8px;">
            <span style="font-size: 0.7rem; letter-spacing: 1px; color: #d4af37; border: 1px solid #d4af37; border-radius: 20px; padding: 4px 12px; background: rgba(212,175,55,0.08);">DATE ADDED</span>
            <span style="font-size: 0.7rem; letter-spacing: 1px; color: rgba(212,175,55,0.4); border: 1px solid rgba(212,175,55,0.2); border-radius: 20px; padding: 4px 12px;">RATING</span>
            <span style="font-size: 0.7rem; letter-spacing: 1px; color: rgba(212,175,55,0.4); border: 1px solid rgba(212,175,55,0.2); border-radius: 20px; padding: 4px 12px;">A–Z</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.watchlist:
        st.markdown("""
        <div class="wl-empty">
            <div class="wl-empty-icon">✦</div>
            <div class="wl-empty-title">Your watchlist is empty.</div>
            <div class="wl-empty-hint">Save films from Recommendation or Explore</div>
        </div>
        """, unsafe_allow_html=True)
        return  
    
    col_info, col_clear = st.columns([4, 1])
    with col_clear:
        if st.button("✕ Clear All", use_container_width=True):
            st.session_state.watchlist = []
            st.session_state.wl_notes = {}
            st.rerun()

    # Grid
    st.markdown('<div class="wl-grid-wrap">', unsafe_allow_html=True)

    titles = st.session_state.watchlist.copy()
    rows = [titles[i:i+5] for i in range(0, len(titles), 5)]

    for row_titles in rows:
        cols = st.columns(5)
        for col, title in zip(cols, row_titles):
            with col:
                match = movies_full[movies_full["title"] == title]
                if not match.empty:
                    movie = match.iloc[0]
                    poster = fetch_poster(int(movie["id"]), api_key)
                    rating = movie.get("vote_average", 0)
                else:
                    poster = FALLBACK_POSTER
                    rating = 0

                st.markdown(f"""
                <div class="wl-poster">
                    <img src="{poster}" alt="{title}" loading="lazy" />
                    <div class="wl-rating">★ {rating:.1f}</div>
                </div>
                <div class="wl-title-text">{title}</div>
                """, unsafe_allow_html=True)

                note_key = f"note_{title}"
                current_note = st.session_state.wl_notes.get(title, "")
                new_note = st.text_input(
                    "Note",
                    value=current_note,
                    placeholder="Why you saved this...",
                    key=note_key,
                    label_visibility="collapsed",
                )
                if new_note != current_note:
                    st.session_state.wl_notes[title] = new_note

                if st.button("✕ Remove", key=f"remove_{title}", use_container_width=True):
                    st.session_state.watchlist.remove(title)
                    if title in st.session_state.wl_notes:
                        del st.session_state.wl_notes[title]
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def show_film_detail(movies_full, movies, similarity, api_key):
    components.html("<script>window.parent.scrollTo(0, 0);</script>", height=0)

    st.markdown("""
    <style>
    .stApp { background-image: none !important; background-color: #060e1a !important; }
    .stApp::before { display: none !important; }
    [data-testid="stMainBlockContainer"] { background-color: #060e1a !important; }
    </style>
    """, unsafe_allow_html=True)

    title = st.session_state.get("selected_film", None)
    if not title:
        st.session_state.current_page = "Home"
        st.rerun()

    # Back button
    if st.button("← Back", key="fd_back"):
        prev = st.session_state.get("film_detail_source", "Explore")
        st.session_state.current_page = prev
        st.rerun()

    # Get movie data from full CSV
    match = movies_full[movies_full["title"].str.strip() == str(title).strip()]
    if match.empty:
        # try partial match
        match = movies_full[movies_full["title"].str.contains(str(title).strip(), case=False, na=False)]
    movie = match.iloc[0]

    # Parse genres
    genres = _parse_genres(movie.get("genres", "[]"))
    genre_pills = "".join([
        f'<span style="font-size:0.68rem; letter-spacing:1px; color:rgba(212,175,55,0.6); border:1px solid rgba(212,175,55,0.2); border-radius:20px; padding:4px 12px;">{g}</span>'
        for g in genres[:4]
    ])

    # Get poster
    movie_id = int(movie.get("id", 0))
    poster = fetch_poster(movie_id, api_key)

    # Parse stats safely
    rating = float(movie.get("vote_average", 0))
    runtime = int(movie.get("runtime", 0)) if str(movie.get("runtime", "")).replace(".","").isdigit() else 0
    budget = movie.get("budget", 0)
    revenue = movie.get("revenue", 0)
    release = str(movie.get("release_date", ""))[:4]
    tagline = movie.get("tagline", "")
    overview = movie.get("overview", "No overview available.")
    language = str(movie.get("original_language", "")).upper()

    def fmt_money(val):
        try:
            v = int(val)
            if v >= 1_000_000_000:
                return f"${v/1_000_000_000:.1f}B"
            elif v >= 1_000_000:
                return f"${v/1_000_000:.0f}M"
            elif v > 0:
                return f"${v:,}"
            else:
                return "N/A"
        except:
            return "N/A"

    # Watchlist state
    in_wl = title in st.session_state.get("watchlist", [])

    # Layout — poster + info
    col_poster, col_info = st.columns([1, 2.5])

    with col_poster:
        st.image(poster, use_container_width=True)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        wl_label = "★ SAVED TO WATCHLIST" if in_wl else "☆ SAVE TO WATCHLIST"
        if st.button(wl_label, key="fd_save", use_container_width=True):
            if in_wl:
                st.session_state.watchlist.remove(title)
            else:
                if "watchlist" not in st.session_state:
                    st.session_state.watchlist = []
                st.session_state.watchlist.append(title)
            st.rerun()

        if st.button("FIND SIMILAR FILMS", key="fd_similar_btn", use_container_width=True):
            st.session_state.current_page = "Recommend"
            st.session_state["rec_select"] = title
            st.rerun()

    with col_info:
        st.markdown(f"""
        <div style="padding: 8px 0 0 16px;">
            <div style="font-size:10px; letter-spacing:4px; color:rgba(212,175,55,0.5); margin-bottom:10px;">
                {release} · {language}
            </div>
            <div style="font-family:'Cormorant Garamond',serif; font-size:2.8rem; font-weight:600; color:#f0d98c; line-height:1.05; margin-bottom:6px;">
                {title}
            </div>
            <div style="font-family:'Cormorant Garamond',serif; font-style:italic; font-size:1rem; color:#6a7a88; margin-bottom:20px;">
                {f'"{tagline}"' if tagline else ''}
            </div>
            <div style="display:flex; align-items:center; gap:16px; margin-bottom:20px; flex-wrap:wrap;">
                <div style="display:flex; align-items:baseline; gap:4px;">
                    <span style="font-size:1.4rem; color:#d4af37; font-weight:600;">{rating:.1f}</span>
                    <span style="font-size:0.75rem; color:rgba(212,175,55,0.4);">/ 10</span>
                </div>
                <div style="width:1px; height:20px; background:rgba(212,175,55,0.15);"></div>
                <span style="font-size:0.78rem; color:#6a7a88; letter-spacing:1px;">{runtime} MIN</span>
                <div style="width:1px; height:20px; background:rgba(212,175,55,0.15);"></div>
                <span style="font-size:0.78rem; color:#6a7a88; letter-spacing:1px;">{fmt_money(budget)} BUDGET</span>
                <div style="width:1px; height:20px; background:rgba(212,175,55,0.15);"></div>
                <span style="font-size:0.78rem; color:#6a7a88; letter-spacing:1px;">{fmt_money(revenue)} REVENUE</span>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:24px;">
                {genre_pills}
            </div>
            <div style="font-size:10px; letter-spacing:3px; color:rgba(212,175,55,0.4); margin-bottom:10px;">OVERVIEW</div>
            <div style="font-size:0.9rem; color:#8a9aa8; line-height:1.75; margin-bottom:28px;">
                {overview}
            </div>
            <div style="height:1px; background:rgba(212,175,55,0.07); margin-bottom:24px;"></div>
            <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:28px;">
                <div style="text-align:center; padding:16px; border:1px solid rgba(212,175,55,0.08); border-radius:8px;">
                    <div style="font-family:'Cormorant Garamond',serif; font-size:1.4rem; color:#d4af37; margin-bottom:4px;">{rating:.1f}</div>
                    <div style="font-size:9px; letter-spacing:2px; color:rgba(212,175,55,0.35);">RATING</div>
                </div>
                <div style="text-align:center; padding:16px; border:1px solid rgba(212,175,55,0.08); border-radius:8px;">
                    <div style="font-family:'Cormorant Garamond',serif; font-size:1.4rem; color:#d4af37; margin-bottom:4px;">{fmt_money(revenue)}</div>
                    <div style="font-size:9px; letter-spacing:2px; color:rgba(212,175,55,0.35);">REVENUE</div>
                </div>
                <div style="text-align:center; padding:16px; border:1px solid rgba(212,175,55,0.08); border-radius:8px;">
                    <div style="font-family:'Cormorant Garamond',serif; font-size:1.4rem; color:#d4af37; margin-bottom:4px;">{runtime}</div>
                    <div style="font-size:9px; letter-spacing:2px; color:rgba(212,175,55,0.35);">MINUTES</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Similar films section
    st.markdown("""
    <div style="padding: 0 0 12px; border-top: 1px solid rgba(212,175,55,0.07); margin-top: 16px;">
        <div style="font-size:10px; letter-spacing:3px; color:rgba(212,175,55,0.4); margin: 24px 0 16px;">YOU MIGHT ALSO LIKE</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        sim_names, sim_posters = recommend(title, movies, similarity, api_key)
        sim_cols = st.columns(5)
        for i, col in enumerate(sim_cols):
            with col:
                st.image(sim_posters[i], use_container_width=True)
                st.markdown(f"""
                <div style="font-size:0.75rem; color:#6a7a88; text-align:center; line-height:1.3; margin-bottom:6px;">
                    {sim_names[i]}
                </div>
                """, unsafe_allow_html=True)
                if st.button("View", key=f"sim_{i}_{sim_names[i]}", use_container_width=True):
                    st.session_state.selected_film = sim_names[i]
                    st.session_state.film_detail_source = "FilmDetail"
                    st.rerun()
    except Exception:
        st.markdown("<div style='color:rgba(212,175,55,0.3); font-size:0.8rem;'>Similar films unavailable.</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)


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
        
        pages = ["Home", "Recommend", "Explore", "Watchlist"]
        for page in pages:
            is_active = st.session_state.current_page == page
            label = f"Watchlist ({len(st.session_state.get('watchlist', []))})" if page == "Watchlist" else page
            if st.button(label, key=f"nav_{page}", use_container_width=True):
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
    @st.cache_data(show_spinner=False)
    def load_movies():
        with open("movies_with_moods.pkl", "rb") as f:
            return pickle.load(f)

    movies = load_movies()
    similarity = load_similarity()
    api_key = get_api_key()
    movies_full = load_movies_full()


    # Route to appropriate page
    if st.session_state.current_page == "Home":
        show_home(movies, api_key)
    elif st.session_state.current_page == "Recommend":
        show_recommend(movies, similarity, api_key)
    elif st.session_state.current_page == "Explore":
        show_explore(movies_full, movies, api_key)
    elif st.session_state.current_page == "Watchlist":
        show_watchlist(movies_full, api_key)
    elif st.session_state.current_page == "FilmDetail":
        show_film_detail(movies_full, movies, similarity, api_key)


if __name__ == "__main__":
    main()