from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests


app = Flask(__name__)

API_KEY = '3e56830b5a0d85f20a5d61476ba98a9a'


def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    response = requests.get(url)

    if response.status_code == 200:
        try:
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return 'https://image.tmdb.org/t/p/w500/' + poster_path
            else:
                return 'https://via.placeholder.com/500x750?text=No+Image+Found'
        except requests.exceptions.JSONDecodeError:
            return 'https://via.placeholder.com/500x750?text=Error+Loading+Image'
    else:
        return 'https://via.placeholder.com/500x750?text=API+Request+Failed'


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters


# Load the movies dictionary and similarity matrix
movies_dict = pickle.load(open('movie_list.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))


@app.route('/', methods=['GET', 'POST'])
def index():
    recommended_movies = []
    recommended_posters = []

    if request.method == 'POST':
        selected_movie_name = request.form.get('movie_name')
        if selected_movie_name:
            recommended_movies, recommended_posters = recommend(selected_movie_name)

    return render_template('index.html', movies=movies['title'].values, recommended_movies=recommended_movies, recommended_posters=recommended_posters, zip=zip)



if __name__ == '__main__':
    app.run(debug=True)
