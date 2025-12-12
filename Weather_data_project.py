import requests
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)

BASE_URL = "https://api.open-meteo.com/v1/forecast"

# List of cities with their coordinates
cities = [
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "New York", "lat": 40.7128, "lon": -74.0060},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"name": "Dubai", "lat": 25.2048, "lon": 55.2708},
    {"name": "Singapore", "lat": 1.3521, "lon": 103.8198},
    {"name": "Berlin", "lat": 52.5200, "lon": 13.4050},
    {"name": "Toronto", "lat": 43.6532, "lon": -79.3832}
]

# ============================================
# STEP 2: Fetch Data from API
# ============================================
def fetch_weather_data(city_info):
    """Fetch weather data for a specific city using Open-Meteo API"""
    params = {
        'latitude': city_info['lat'],
        'longitude': city_info['lon'],
        'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
        'timezone': 'auto'
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {city_info['name']}: {e}")
        return None

# Weather code descriptions
weather_codes = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Foggy",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with hail"
}

def get_weather_description(code):
    """Get weather description from code"""
    return weather_codes.get(code, "Unknown")

# Collect data for all cities
weather_data = []
print("Fetching weather data from Open-Meteo (No API key needed)...")
print("=" * 60)

for city_info in cities:
    print(f"Fetching data for {city_info['name']}...")
    data = fetch_weather_data(city_info)
    
    if data and 'current' in data:
        current = data['current']
        weather_info = {
            'City': city_info['name'],
            'Temperature (°C)': current.get('temperature_2m', 0),
            'Humidity (%)': current.get('relative_humidity_2m', 0),
            'Wind Speed (m/s)': current.get('wind_speed_10m', 0),
            'Weather Code': current.get('weather_code', 0),
            'Weather': get_weather_description(current.get('weather_code', 0)),
            'Latitude': city_info['lat'],
            'Longitude': city_info['lon']
        }
        # Add "Feels Like" as approximation (Temperature - wind chill factor)
        wind_chill = weather_info['Wind Speed (m/s)'] * 0.5
        weather_info['Feels Like (°C)'] = weather_info['Temperature (°C)'] - wind_chill
        
        weather_data.append(weather_info)
        print(f"  ✓ {city_info['name']}: {weather_info['Temperature (°C)']}°C, {weather_info['Weather']}")

# Create DataFrame
df = pd.DataFrame(weather_data)

if df.empty:
    print("\n❌ ERROR: No data was fetched. Please check your internet connection.")
    exit()

print("\n" + "="*60)
print("DATA FETCHED SUCCESSFULLY!")
print("="*60)
print(df[['City', 'Temperature (°C)', 'Humidity (%)', 'Wind Speed (m/s)', 'Weather']])

# ============================================
# STEP 3: Create Visualizations
# ============================================

# Create a dashboard with multiple subplots
fig = plt.figure(figsize=(16, 12))
fig.suptitle('Weather Data Visualization Dashboard\n(Real-time data from Open-Meteo API)', 
             fontsize=20, fontweight='bold', y=0.995)

# 1. Bar Chart - Temperature by City
ax1 = plt.subplot(2, 3, 1)
colors = plt.cm.RdYlBu_r((df['Temperature (°C)'].values - df['Temperature (°C)'].min()) / 
                         (df['Temperature (°C)'].max() - df['Temperature (°C)'].min()))
bars = ax1.bar(df['City'], df['Temperature (°C)'], color=colors, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('City', fontweight='bold')
ax1.set_ylabel('Temperature (°C)', fontweight='bold')
ax1.set_title('Temperature by City', fontweight='bold', pad=10)
ax1.tick_params(axis='x', rotation=45)
ax1.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}°C', ha='center', va='bottom', fontsize=8)

# 2. Scatter Plot - Temperature vs Humidity
ax2 = plt.subplot(2, 3, 2)
scatter = ax2.scatter(df['Temperature (°C)'], df['Humidity (%)'], 
                     s=200, c=df['Temperature (°C)'], cmap='coolwarm', 
                     edgecolors='black', linewidth=1.5, alpha=0.7)
for i, city in enumerate(df['City']):
    ax2.annotate(city, (df['Temperature (°C)'].iloc[i], df['Humidity (%)'].iloc[i]),
                fontsize=8, ha='right', xytext=(-5, 0), textcoords='offset points')
ax2.set_xlabel('Temperature (°C)', fontweight='bold')
ax2.set_ylabel('Humidity (%)', fontweight='bold')
ax2.set_title('Temperature vs Humidity', fontweight='bold', pad=10)
ax2.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax2, label='Temperature (°C)')

# 3. Horizontal Bar Chart - Humidity Levels
ax3 = plt.subplot(2, 3, 3)
df_sorted = df.sort_values('Humidity (%)')
colors_humidity = plt.cm.Blues(df_sorted['Humidity (%)'].values / 100)
bars_h = ax3.barh(df_sorted['City'], df_sorted['Humidity (%)'], 
                   color=colors_humidity, edgecolor='black', linewidth=1.5)
ax3.set_xlabel('Humidity (%)', fontweight='bold')
ax3.set_ylabel('City', fontweight='bold')
ax3.set_title('Humidity Levels by City', fontweight='bold', pad=10)
ax3.grid(axis='x', alpha=0.3)

# Add value labels
for bar in bars_h:
    width = bar.get_width()
    ax3.text(width, bar.get_y() + bar.get_height()/2.,
             f'{width:.0f}%', ha='left', va='center', fontsize=8, 
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

# 4. Line Plot - Wind Speed Comparison
ax4 = plt.subplot(2, 3, 4)
ax4.plot(df['City'], df['Wind Speed (m/s)'], marker='o', linewidth=2, 
         markersize=8, color='darkgreen', markerfacecolor='lightgreen', 
         markeredgecolor='black', markeredgewidth=1.5)
ax4.set_xlabel('City', fontweight='bold')
ax4.set_ylabel('Wind Speed (m/s)', fontweight='bold')
ax4.set_title('Wind Speed Comparison', fontweight='bold', pad=10)
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True, alpha=0.3)
ax4.fill_between(range(len(df)), df['Wind Speed (m/s)'], alpha=0.3, color='lightgreen')

# 5. Pie Chart - Weather Conditions Distribution
ax5 = plt.subplot(2, 3, 5)
weather_counts = df['Weather'].value_counts()
colors_pie = plt.cm.Set3(range(len(weather_counts)))
wedges, texts, autotexts = ax5.pie(weather_counts.values, labels=weather_counts.index, 
                                     autopct='%1.1f%%', startangle=90, colors=colors_pie,
                                     explode=[0.05]*len(weather_counts), shadow=True)
ax5.set_title('Weather Conditions Distribution', fontweight='bold', pad=10)
for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(9)

# 6. Grouped Bar Chart - Temperature vs Feels Like
ax6 = plt.subplot(2, 3, 6)
x = range(len(df))
width = 0.35
bars1 = ax6.bar([i - width/2 for i in x], df['Temperature (°C)'], 
                width, label='Actual Temp', color='coral', edgecolor='black', linewidth=1.5)
bars2 = ax6.bar([i + width/2 for i in x], df['Feels Like (°C)'], 
                width, label='Feels Like', color='skyblue', edgecolor='black', linewidth=1.5)
ax6.set_xlabel('City', fontweight='bold')
ax6.set_ylabel('Temperature (°C)', fontweight='bold')
ax6.set_title('Actual Temperature vs Feels Like', fontweight='bold', pad=10)
ax6.set_xticks(x)
ax6.set_xticklabels(df['City'], rotation=45, ha='right')
ax6.legend(loc='best')
ax6.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('weather_dashboard.png', dpi=300, bbox_inches='tight')
print("\n✓ Dashboard saved as 'weather_dashboard.png'")
plt.show()

# ============================================
# STEP 4: Additional Statistics
# ============================================
print("\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60)
print(f"\nAverage Temperature: {df['Temperature (°C)'].mean():.2f}°C")
print(f"Highest Temperature: {df['Temperature (°C)'].max():.2f}°C ({df.loc[df['Temperature (°C)'].idxmax(), 'City']})")
print(f"Lowest Temperature: {df['Temperature (°C)'].min():.2f}°C ({df.loc[df['Temperature (°C)'].idxmin(), 'City']})")
print(f"\nAverage Humidity: {df['Humidity (%)'].mean():.2f}%")
print(f"Average Wind Speed: {df['Wind Speed (m/s)'].mean():.2f} m/s")

print("\n" + "="*60)
print("TASK COMPLETED SUCCESSFULLY! ✓")
print("="*60)
print("\n📊 Your dashboard includes:")
print("  1. Temperature bar chart")
print("  2. Temperature vs Humidity scatter plot")
print("  3. Humidity levels horizontal bar chart")
print("  4. Wind speed line chart")
print("  5. Weather conditions pie chart")
print("  6. Actual vs Feels Like temperature comparison")
print("\n💾 File saved: weather_dashboard.png")