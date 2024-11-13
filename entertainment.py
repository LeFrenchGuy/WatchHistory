  
from movie_entry import MovieEntry
from tmdbv3api import TMDb, Movie, TV
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os  # Import the os module for file and directory operations
import json
from constants import TMDB_API_KEY
import re

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
not_found_titles = []

def clean_title_and_extract_date(line):
    """Clean title, extract date, and check for cinema label."""
    # Default values
    title = ''
    date = ''
    is_cinema = False

    # Try to match a date pattern and the cinema label in the line
    date_pattern = r"\((\d{2}-\d{2})\)"  # Pattern for dates like (mm-dd)
    cinema_pattern = r"\(cinema\)"

    # Search for the date and cinema pattern in the line
    date_match = re.search(date_pattern, line)
    cinema_match = re.search(cinema_pattern, line, re.IGNORECASE)  # Case-insensitive search

    # If a date is found, extract it
    if date_match:
        date = date_match.group(1)  # Extract date (mm-dd)
        line = line.replace(date_match.group(0), "")  # Remove the date from the title

    # Check if "cinema" exists and remove it
    if cinema_match:
        is_cinema = True
        line = line.replace(cinema_match.group(0), "").strip()  # Remove "(cinema)"

    # Clean the title, strip excess whitespace, and capitalize properly
    title = line.strip().title()

    return title, date, is_cinema

def fetch_tmdb_details(title):
  """Fetch genres, runtime, and type (movie or TV) using TMDb."""
  try:

     # Check if the title is in the cache
    if title in cache:
      return cache[title]
    
    # Search for both movies and TV shows
    movie_results = movie_api.search(title)
    tv_results = tv_api.search(title)

    # Prioritize movies, fallback to TV shows
    if movie_results and movie_results.total_results > 0:
      item = movie_results[0]
      details = movie_api.details(item.id)
      kind = "movie"
    elif tv_results and tv_results.total_results > 0:
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
    runtime = getattr(details, 'runtime', 0)  # Runtime in minutes (0 if unavailable)
    if runtime == 0:
       print(f"Runtime missing for '{title}' ({kind})")
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
    print(f"An error occurred while fetching data for '{title}': {e}")
    return None
  
with open(filename, 'r', encoding='utf-8') as file:
    for line in file:
        # Strip leading/trailing whitespace
        line = line.strip()

        # Find the first occurrence of '(' for date extraction
        if '(' in line and ')' in line:
            title, date, is_cinema = clean_title_and_extract_date(line)
        else:
            continue  

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
    enhanced_data.append({
        "Title": entry.title,
        "Date_Watched": entry.date,
        "Genres": details['Genres'],
        "Runtime": details['Runtime'],
        "Type": details['Type']
    })
  else:
    not_found_titles.append(entry.title)

if not_found_titles:
    print("The following titles could not be fetched:")
    print("\n".join(not_found_titles))

df = pd.DataFrame(enhanced_data)
# Display the initial data for verification
print(df.head())

YEAR = "2024"

# Add the year to 'Date_Watched' before converting to datetime
df['Date_Watched'] = df['Date_Watched'].apply(lambda x: f"{YEAR}-{x}" if pd.notna(x) and '-' in x else x)

# Convert 'Date_Watched' to datetime
df['Date_Watched'] = pd.to_datetime(df['Date_Watched'], format='%Y-%m-%d', errors='coerce')

# Check for invalid dates
invalid_dates = df[df['Date_Watched'].isna()]
if not invalid_dates.empty:
  print("The following entries have invalid or missing dates:")
  print(invalid_dates[['Title', 'Date_Watched']])

# Add Month and Week columns for analysis
df['Month'] = df['Date_Watched'].dt.month
df['Week'] = df['Date_Watched'].dt.isocalendar().week

# Display the cleaned and augmented data
print(df.head())

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