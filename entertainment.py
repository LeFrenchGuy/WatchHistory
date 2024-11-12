  
from movie_entry import MovieEntry
from tmdbv3api import TMDb, Movie, TV
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os  # Import the os module for file and directory operations
import json
from constants import TMDB_API_KEY

filename = "entertainment.txt"
db_path = "com.plexapp.plugins.library.db"
CACHE_FILE = "movie_cache.json"
# Ensure the cache file exists
if not os.path.exists(CACHE_FILE):
  with open(CACHE_FILE, 'w') as f:
    json.dump({}, f)

# Load the cache
with open(CACHE_FILE, 'r') as f:
  cache = json.load(f)

data = []
# Initialize IMDb API
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY

movie_api = Movie()
tv_api = TV()


# Initial data (abbreviated example for runtime)
entries = []

def fetch_tmdb_details(title):
  """Fetch genres, runtime, and type (movie or TV) using TMDb."""
  try:

     # Check if the title is in the cache
    if title in cache:
      print(f"Found '{title}' in cache.")
      return cache[title]
    
    # Search for both movies and TV shows
    movie_results = movie_api.search(title)
    tv_results = tv_api.search(title)

    # Prioritize movies, fallback to TV shows
    if movie_results:
      item = movie_results[0]
      details = movie_api.details(item.id)
      kind = "movie"
    elif tv_results:
      item = tv_results[0]
      details = tv_api.details(item.id)
      kind = "tv"
    else:
      # Cache the absence of data to prevent redundant API calls
      print(f"No results found for '{title}'. Caching as None.")
      cache[title] = None
      with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)
      return None

    # Extract genres, runtime, and type
    genres = [genre['name'] for genre in details.genres]
    runtime = details.runtime or 0  # Runtime in minutes (0 if unavailable)
    print("genres:") 
    print(genres) 
    print("runtime:") 
    print(runtime) 
    print("kind:") 
    print(kind) 

    data = {
        'Genres': genres,
        'Runtime': runtime,
        'Type': kind
    }

    # Save the fetched data to the cache
    cache[title] = data
    with open(CACHE_FILE, 'w') as f:
      json.dump(cache, f, indent=2)

    return data


  except Exception as e:
    print(f"Error fetching details for {title}: {e}")
    return None
  
with open(filename, 'r') as file:
    for line in file:
        # Strip leading/trailing whitespace
        line = line.strip()

        # Find the first occurrence of '(' for date extraction
        if '(' in line and ')' in line:
            title, rest = line.split(" (", 1)
            date = rest.split(")")[0].strip()  # Extract date from the first parenthesis
            # Check if "cinema" exists in the remaining part of the line
            is_cinema = "cinema" in rest.lower()
        else:
            # If no parentheses are found, assume the whole line is the title with no date or cinema info
            title = line
            date = ""
            is_cinema = False

        # Capitalize title and strip extra spaces
        title = title.title().strip()

        # Create a MovieEntry object and add it to the list
        movie_entry = MovieEntry(title, date, is_cinema)
        entries.append(movie_entry)


# Enrich data with additional information
enhanced_data = []
for entry in entries:
  details = fetch_tmdb_details(entry.title)
  if details:
    print("details:") 
    print(details) 
    enhanced_data.append({
        "Title": entry.title,
        "Date_Watched": entry.date,
        "Genres": details['Genres'],
        "Runtime": details['Runtime'],
        "Type": details['Type']
    })
  else:
    print(f"No details found for {title}.")


df = pd.DataFrame(enhanced_data)

# Convert 'Date_Watched' to datetime and add month/week columns
df['Date_Watched'] = pd.to_datetime(df['Date_Watched'], errors='coerce')
df['Month'] = df['Date_Watched'].dt.month
#df['Week'] = df['Date_Watched'].dt.isocalendar().week


# Display the initial data for verification
print(df.head())

"""
# Genre distribution
genre_counts = df.explode('Genres').groupby('Genres').size()
type_counts = df.groupby('Type').size()
monthly_runtime = df.groupby('Month')['Runtime'].sum()
#weekly_runtime = df.groupby('Week')['Runtime'].sum()

# Plotting genre distribution
plt.figure(figsize=(10, 6))
genre_counts.sort_values(ascending=False).plot(kind='bar', color='skyblue')
plt.title("Distribution of Watched Genres")
plt.ylabel("Count")
plt.xlabel("Genres")
plt.xticks(rotation=45)
plt.show()

# Plotting type distribution
plt.figure(figsize=(6, 4))
type_counts.plot(kind='bar', color='coral')
plt.title("Movies vs TV Shows Watched")
plt.ylabel("Count")
plt.xlabel("Type")
plt.xticks(rotation=0)
plt.show()

# Plotting monthly runtime
plt.figure(figsize=(10, 6))
monthly_runtime.plot(kind='line', marker='o', color='green')
plt.title("Total Runtime Watched Per Month")
plt.ylabel("Total Runtime (minutes)")
plt.xlabel("Month")
plt.xticks(range(1, 13))
plt.grid(True)
plt.show()

# Plotting weekly runtime
# plt.figure(figsize=(10, 6))
# weekly_runtime.plot(kind='line', marker='o', color='purple')
# plt.title("Total Runtime Watched Per Week")
# plt.ylabel("Total Runtime (minutes)")
# plt.xlabel("Week")
# plt.grid(True)
# plt.show()
"""