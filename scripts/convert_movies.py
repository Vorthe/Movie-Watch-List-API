import json

with open("movies.json", "r", encoding="utf-8") as f:
    movies = json.load(f)

new_movies = []

for movie in movies:
    new_movies.append(
        {
            "title": movie["title"],
            "description": "IMDb Top Movie",
            "rating": 10,
            "watched": False,
            "genre": "Drama",
            "owner_id": 1,
        }
    )

with open("movies_seed.json", "w", encoding="utf-8") as f:
    json.dump(new_movies, f, indent=4)

print("Done")
