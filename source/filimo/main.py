from database import get_db_connection, close_db_connection, get_movies, update_movie_status
from proccessmovie import proccessMovie

conn = get_db_connection()

result = get_movies(conn)

for movie in result:
    if (movie[6] == ''):
        update_movie_status(conn, movie[1], 'downloading')
        result = proccessMovie(movie[1])
        if result:
            update_movie_status(conn, movie[1], 'done')
        else:
            update_movie_status(conn, movie[1], 'failed')
    else:
        print('SKIP: ' + movie[1] + ' - ' + movie[6])

close_db_connection(conn)