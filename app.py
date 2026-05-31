import os
import pickle
from pathlib import Path
import gdown

import pandas as pd
import requests
import streamlit as st

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
FALLBACK_POSTER = "https://placehold.co/500x750/1b1f3b/f2f3f7?text=No+Poster"

FILE_ID = "1TPM1vM1UqpZEOYXpIugNtpJddPj6Yo9n"  # Google Drive file ID for similarity.pkl

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


def fetch_poster(movie_id: int, api_key: str) -> str:
    """Fetches poster URL from TMDB. Returns fallback image on failure."""
    if not api_key:
        return FALLBACK_POSTER

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": api_key}

    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
    except requests.RequestException:
        pass

    return FALLBACK_POSTER


def recommend(movie: str, movies: pd.DataFrame, similarity_matrix, api_key: str):
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


st.set_page_config(page_title="Movie Recommender", page_icon=":movie_camera:", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #f7f3ec, #e6eef5 45%, #dce5ef);
    }
    .hero {
        background: linear-gradient(120deg, #0f4c5c, #2f6690);
        border-radius: 16px;
        padding: 24px;
        color: #f6f8fb;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(15, 76, 92, 0.22);
    }
    .hero h1 {
        margin: 0;
        font-size: 2rem;
    }
    .hero p {
        margin-top: 8px;
        opacity: 0.92;
    }
    .movie-title {
        font-weight: 650;
        color: #0f172a;
        text-align: center;
        margin-top: 8px;
        min-height: 48px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Movie Recommender System</h1>
        <p>Pick a movie you like.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

movies = load_movies()
similarity = load_similarity()
api_key = get_api_key()

if not api_key:
    st.warning("TMDB API key not found. Add TMDB_API_KEY in your .env file.")

selected_movie_name = st.selectbox("Choose a movie", movies["title"].values)

if st.button("Recommend Movies", type="primary", use_container_width=True):
    with st.spinner("Finding great matches for you..."):
        try:
            names, posters = recommend(selected_movie_name, movies, similarity, api_key)
            columns = st.columns(5)
            for idx, col in enumerate(columns):
                with col:
                    st.image(posters[idx], use_container_width=True)
                    st.markdown(f"<div class='movie-title'>{names[idx]}</div>", unsafe_allow_html=True)
        except Exception as ex:
            st.error(f"Unable to generate recommendations: {ex}")