# 🚗 Onroad - Vehicle Breakdown Assistance

A web-based application that assists users facing vehicle breakdowns by connecting them with nearby mechanics in real-time.

## Features

- **🔧 User Booking** - Request breakdown assistance with GPS location
- **📍 Real-Time Location** - Google Maps integration for live tracking
- **🔔 Mechanic Notifications** - Mechanics receive and can accept/reject requests
- **🗺️ Live Tracking** - Track mechanic's arrival in real-time
- **📱 Responsive Design** - Works on desktop and mobile devices

## Tech Stack

- **Backend:** Python (Flask)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Maps:** Google Maps API

## Installation

```bash
# Clone the repository
git clone https://github.com/whiteblue-suriya/Onroad-Vehicle-breakdown-Assistance.git
cd Onroad-Vehicle-breakdown-Assistance

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the application
python app.py
```

Open your browser and navigate to: **http://localhost:5000**

## Project Structure

```
onroad _vechile_ breakdown/
├── app.py                  # Flask backend with routes & database
├── requirements.txt        # Python dependencies
├── onroad.db              # SQLite database (auto-created)
└── templates/
    ├── index.html              # Home page
    ├── user_register.html      # User registration
    ├── mechanic_register.html  # Mechanic registration
    ├── booking.html            # Request help page
    ├── track_booking.html      # Live tracking page
    └── mechanic_dashboard.html # Mechanic dashboard
```

## How It Works

1. **User Registration** - Users register with their vehicle details
2. **Request Help** - Submit a breakdown request with current GPS location
3. **Mechanic Response** - Nearby mechanics receive the request and can accept or reject
4. **Live Tracking** - User can track the mechanic's location in real-time on the map

## Google Maps API Setup

Replace `YOUR_API_KEY` in the following files with your Google Maps API key:
- `templates/booking.html`
- `templates/track_booking.html`
- `templates/mechanic_dashboard.html`

## Screenshots

The application features a modern dark theme with:
- Glassmorphism UI design
- Professional color scheme (blue/green accents)
- Workshop-themed background images

## License

MIT License
