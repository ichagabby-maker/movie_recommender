import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('TMDB_API_KEY')

from flask import Flask, request, render_template
import requests
import pandas as pd
import pickle
app = Flask(__name__)
# loading models
# movies = pd.read_csv('movies.csv')
movies = pickle.load(open('model.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
# function to fetch movie poster
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        data = requests.get(url, timeout=5)
        data.raise_for_status()
        data = data.json()
        
        if data.get('poster_path'):
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        return None
    except Exception as e:
        print(f"Error fetching poster: {e}")
        return None
# function to get recommended movies
def get_recommendations(movie):
    try:
        idx = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], []
    # get pairwise similarity scores of all movies with the selected movie
    sim_scores = list(enumerate(similarity[idx]))
    # sort the movies based on similarity scores in descending order
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # get top 20 similar movies (excluding the selected movie)
    sim_scores = sim_scores[1:21]
    # get titles and posters of the recommended movies
    movie_indices = [i[0] for i in sim_scores]
    movie_titles = movies['title'].iloc[movie_indices].tolist()
    movie_posters = [fetch_poster(movies['id'].iloc[i]) for i in movie_indices]
    return movie_titles, movie_posters
# home page
@app.route('/')
def home():
    movie_list = movies['title'].tolist()
    return render_template('index.html', movie_list=movie_list)
# recommendation page
@app.route('/recommend', methods=['POST'])
def recommend():
    movie_title = request.form['selected_movie']
    recommended_movie_titles, recommended_movie_posters = get_recommendations(movie_title)
    return render_template('index.html', movie_list=movies['title'].tolist(),
                           recommended_movie_titles=recommended_movie_titles,
                           recommended_movie_posters=recommended_movie_posters)

if __name__ == '__main__':
    app.run(debug=True)