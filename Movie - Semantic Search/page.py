import streamlit as st
from search import get_directors, get_genres, get_movie_stars, search_movies, display_movies
import requests
import pandas as pd
from semantic import semantic_search
from langchain.vectorstores import FAISS


image_path = "mt.png"
st.image(image_path, use_column_width=True)
st.title("Movie Recommender")



st.write("Welcome to Movie Recommender! Discover new movies based on your preferences.")



st.sidebar.title("Your Preferences")

genre_options = get_genres()
selected_genre = st.sidebar.multiselect("Genre", genre_options, default=["Action"])
release_date_range = st.sidebar.slider("Release Date", 1930, 2023, (2003, 2023))
imdb_ratings_range = st.sidebar.slider("IMDB Ratings", 0.0, 10.0, (6.4, 8.2))
duration_range = st.sidebar.slider("Duration", 0, 300, (60, 180))
directors_options = get_directors()
directors = st.sidebar.multiselect("Director", directors_options, default=["Christopher Nolan"])
cast_options = get_movie_stars()
selected_cast = st.sidebar.multiselect("Cast", cast_options, default=["Tom Hardy"])


user_text_input = st.sidebar.text_area("Additional Comments", "")

search_button_key = "search_button_key"  
if st.sidebar.button("Search", key=search_button_key):
    preferences = {
        'Genre': selected_genre,
        'Year': release_date_range,
        'IMDB_Rating': imdb_ratings_range,
        'Runtime': duration_range,
        'Director': directors,
        'Cast': selected_cast,
    }

    if user_text_input:
        preferences['UserText'] = user_text_input

    results = search_movies(preferences, user_text_input)

    if results:
        display_movies(results)






