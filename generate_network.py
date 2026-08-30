import os
import requests
from datetime import datetime, timedelta

USERNAME = os.getenv("GITHUB_USERNAME", "saptarshiboni-arch")
TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

# Get contribution data
query = """
query($user:String!) {
  user(login:$user) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""

response = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": {"user": USERNAME}},
    headers=headers,
)

data = response.json()

weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

# Flatten contribution days
days = []

for week in weeks:
    for day in week["contributionDays"]:
        days.append(day)

# SVG settings
width = 900
height = 420

svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
width="{width}" height="{height}"
viewBox="0 0 {width} {height}">

<defs>
  <filter id="glow">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>

  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#050505"/>
    <stop offset="100%" stop-color="#101820"/>
  </linearGradient>
</defs>

<rect width="100%" height="100%" rx="20" fill="url(#bg)"/>

<text x="450" y="38"
      text-anchor="middle"
      fill="#ffffff"
      font-size="22"
      font-family="Arial"
      font-weight="bold">
  🧠 AI Contribution Network
</text>
'''

# Display last 364 days
days = days[-364:]

cols = 52
rows = 7

cell = 12
gap = 5

start_x = 45
start_y = 75

points = []

for i, day in enumerate(days):

    col = i // rows
    row = i % rows

    x = start_x + col * (cell + gap)
    y = start_y + row * (cell + gap)

    count = day["contributionCount"]

    if count == 0:
        opacity = 0.12
        radius = 3
    elif count < 3:
        opacity = 0.4
        radius = 4
    elif count < 7:
        opacity = 0.7
        radius = 5
    else:
        opacity = 1
        radius = 6

    cx = x + cell / 2
    cy = y + cell / 2

    points.append((cx, cy, count))

# Draw connections first
for i in range(len(points)):
    x1, y1, c1 = points[i]

    if c1 == 0:
        continue

    # Connect to nearby active nodes
    for j in range(i + 1, min(i + 8, len(points))):
        x2, y2, c2 = points[j]

        if c2 == 0:
            continue

        distance = ((x2-x1)**2 + (y2-y1)**2) ** 0.5

        if distance < 35:

            svg += f'''
            <line x1="{x1}" y1="{y1}"
                  x2="{x2}" y2="{y2}"
                  stroke="#00ff88"
                  stroke-opacity="0.22"
                  stroke-width="1"/>
            '''

# Draw nodes
for x, y, count in points:

    if count == 0:
        fill = "#243238"
        opacity = "0.35"
        r = 3
    elif count < 3:
        fill = "#00d9ff"
        opacity = "0.65"
        r = 4
    elif count < 7:
        fill = "#00ff88"
        opacity = "0.85"
        r = 5
    else:
        fill = "#ff4fd8"
        opacity = "1"
        r = 6

    svg += f'''
    <circle cx="{x}" cy="{y}"
            r="{r}"
            fill="{fill}"
            fill-opacity="{opacity}"
            filter="url(#glow)">
      <animate attributeName="r"
               values="{r};{r+2};{r}"
               dur="2s"
               repeatCount="indefinite"/>
    </circle>
    '''

svg += '''
</svg>
'''

# Create assets directory
os.makedirs("assets", exist_ok=True)

with open(
    "assets/github-ai-contribution-network.svg",
    "w",
    encoding="utf-8"
) as f:
    f.write(svg)

print("AI Contribution Network generated successfully!")
