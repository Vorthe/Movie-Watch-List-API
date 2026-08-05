import json

from App.database import SessionLocal
from App.models import Movies

db = SessionLocal()

with open("movies_seed.json", "r", encoding="utf-8") as file:
    movies = json.load(file)

for movie_data in movies:
    movie = Movies(**movie_data)
    db.add(movie)

db.commit()
db.close()

print("100 movies inserted successfully")
