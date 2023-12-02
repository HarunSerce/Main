import pandas as pd
import psycopg2
import streamlit as st
from semantic import semantic_search
from streamlit.components.v1 import declare_component



def build_sql_query(preferences):
    sql_query_parts = []
    args = []

    for key, value in preferences.items():
        if key == 'Genre' and value:
            genre_conditions = ' OR '.join([f'"Genre" LIKE %s' for _ in value])
            sql_query_parts.append(f'({genre_conditions})')
            args.extend([f"%{genre}%" for genre in value])
        elif key == 'Year':
            sql_query_parts.append('"Year" BETWEEN %s AND %s')
            args.extend(value)
        elif key == 'IMDB_Rating':
            sql_query_parts.append('"Rating" BETWEEN %s AND %s')
            args.extend(value)
        elif key == 'Runtime':
            sql_query_parts.append('"Duration" BETWEEN %s AND %s')
            args.extend(value)
        elif key == 'Director' and value:
            director_conditions = ' OR '.join([f'movieset."Director" = %s' for _ in value])
            sql_query_parts.append(f'({director_conditions})')
            args.extend(value)
        elif key == 'Cast' and value:
 
            full_cast_condition = ' AND '.join([f'movieset."Cast" LIKE %s' for _ in value])
            sql_query_parts.append(f'({full_cast_condition})')
            args.extend([f"%{cast}%" for cast in value])

            cast_conditions = ' OR '.join([f'movieset."Cast" LIKE %s' for _ in value])
            sql_query_parts.append(f'({cast_conditions})')
            args.extend([f"%{cast}%" for cast in value])

    full_query = f'SELECT * FROM "Imdb".movieset WHERE {" AND ".join(sql_query_parts)}'
    print(full_query)
    print(args)

    return sql_query_parts, args

def search_movies(preferences, user_text):
    columnnames = ['ID', 'Poster', 'Movie', 'Year', 'Duration', 'Genre', 'Rating', 'Description', 'Director', 'Cast', 'Votes']

    
    sql_query, args = build_sql_query(preferences)
    semantic_ids = semantic_search(user_text)


    db_params = {
        'database': 'database',
        'user': 'username',
        'password': 'db password',
        'host': 'hostname',
        'port': 'port'
    }

    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()

    result_df = pd.DataFrame(columns=columnnames)

    try:
        # Full Query
        full_query = f'SELECT * FROM "Imdb".movieset WHERE {" AND ".join(sql_query)}'

        if not semantic_ids:  # Semantic IDs boşsa
            cursor.execute(full_query, tuple(args))
            results = cursor.fetchall()
            result_df = pd.DataFrame(results, columns=['ID', 'Poster', 'Movie', 'Year', 'Duration', 'Genre', 'Rating', 'Description', 'Director', 'Cast', 'Votes'])
        else:
            # Semantic Query
            id_sql_query = ' OR '.join([f'"ID" = %s' for _ in semantic_ids])
            semantic_sql_query = f'SELECT * FROM "Imdb".movieset WHERE {id_sql_query}'
            cursor.execute(semantic_sql_query, tuple(semantic_ids))
            semantic_results = cursor.fetchall()
            semantic_df = pd.DataFrame(semantic_results, columns=['ID', 'Poster', 'Movie', 'Year', 'Duration', 'Genre', 'Rating', 'Description', 'Director', 'Cast', 'Votes'])

            # SQL Query
            full_query = f'SELECT * FROM "Imdb".movieset WHERE {" AND ".join(sql_query)}'
            cursor.execute(full_query, tuple(args))
            sql_results = cursor.fetchall()
            sql_df = pd.DataFrame(sql_results, columns=['ID', 'Poster', 'Movie', 'Year', 'Duration', 'Genre', 'Rating', 'Description', 'Director', 'Cast', 'Votes'])

            common_ids = set(semantic_df['ID']).intersection(set(sql_df['ID']))

            if common_ids:  # Ortak ID'ler varsa
                result_df = pd.concat([semantic_df[semantic_df['ID'].isin(common_ids)], result_df[result_df['ID'].isin(common_ids)]], ignore_index=True)
            else:
                result_df = pd.DataFrame(semantic_results, columns=['ID', 'Poster', 'Movie', 'Year', 'Duration', 'Genre', 'Rating', 'Description', 'Director', 'Cast', 'Votes'])

        if not result_df.empty:
            for index, row in result_df.iterrows():
                display_movies(row)

    except Exception as e:
        print(f"Error executing SQL query: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()

# to fetch lists of genres,director's name, cast I created functions below

def get_genres():
    db_params = {
        'database': 'database',
        'user': 'username',
        'password': 'db password',
        'host': 'hostname',
        'port': 'port'
    }

    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT "Genre" FROM "Imdb".movieset;
    """)
    genres = [genre.strip() for row in cursor.fetchall() for genre in row[0].split(',')]

    genres = list(set(genres))

    connection.close()
    return genres

def get_directors():
    db_params = {
        'database': 'database',
        'user': 'username',
        'password': 'db password',
        'host': 'hostname',
        'port': 'port'
    }

    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT "Director" FROM "Imdb".movieset;
    """)
    directors = [director.strip() for row in cursor.fetchall() for director in row[0].split(',')]
    directors = list(set(directors))

    connection.close()
    return directors

def get_movie_stars():    
    db_params = {
        'database': 'database',
        'user': 'username',
        'password': 'db password',
        'host': 'hostname',
        'port': 'port'
    }

    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
   
    cursor.execute("""
        SELECT DISTINCT "Cast" FROM "Imdb".movieset;
    """)
    stars = [star.strip() for row in cursor.fetchall() for star in row[0].split(',')]
    stars = list(set(stars))

    connection.close()
    return stars

# A function to display results on UI

def display_movies(movie_info):

    st.title("")


    st.markdown(
        """
        <style>
            .reportview-container {
                background: #333333;  /* tone of grey */
                color: white;  /* provide a color for text */
            }
        </style>
        """,
        unsafe_allow_html=True
    )


    col1, col2 = st.columns([1, 2])


    with col1:
        st.image(movie_info['Poster'], caption='Movie Poster', width=150)

    with col2:
        st.subheader(movie_info['Movie'])
        st.write(f"**Year:** {movie_info['Year']}")
        st.write(f"**Duration:** {movie_info['Duration']} minutes")
        st.write(f"**Genre:** {movie_info['Genre']}")
        st.write(f"**Rating:** {movie_info['Rating']}")
        st.write(f"**Description:** {movie_info['Description']}")
        st.write(f"**Director:** {movie_info['Director']}")
        st.write(f"**Cast:** {movie_info['Cast']}")
        st.write(f"**Votes:** {movie_info['Votes']}")

    st.markdown("___________")    
