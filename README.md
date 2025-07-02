# 🚆 Bangladesh Railway Train Seat Matrix Web Application

A comprehensive web application to **visualize segmented seat availability and fare matrices** for Bangladesh Railway trains. This version focuses on **direct and segmented ticketing analysis, smart routing algorithms, and real-time availability tracking** — built using Flask + Vanilla JS + REST APIs.

✨ **Key Features:**
- 🧮 **Segmented Seat Matrix**: View seat availability across all route segments for any train
- 🎯 **Smart Route Finding**: Direct, segmented, and mixed-class ticketing options
- 📊 **Fare Matrix Visualization**: Complete fare breakdown by seat class and route
- 🗓️ **Date-Aware Journey Planning**: Handles overnight journeys with proper date segmentation
- 🚄 **Complete Train Coverage**: All 120+ Bangladesh Railway trains supported
- 📱 **Mobile-Optimized Interface**: Fully responsive design for all devices
- ⚡ **Zero Authentication Required**: No login needed for basic functionality
- ⏳ **Queue System**: Intelligent request management to prevent API overload

---

## 🌐 Live Site

👉 **Live URL:** [seat.onrender.com](https://seat.onrender.com)  
⚠️ **Note:** First load may be delayed up to 1 minute due to free-tier cold starts.

| <img src="images/Screenshot_1.png" width="400"> | <img src="images/Screenshot_2.png" width="400"> |
|--------------------------------------------------|--------------------------------------------------|
| <div align="center">**Seat Matrix Interface**</div>     | <div align="center">**Train Route View**</div>   |

---

<div align="center">
  <a href="https://youtu.be/zG55QW73N0c">
    <img src="https://img.youtube.com/vi/zG55QW73N0c/hqdefault.jpg" alt="Watch the Video" width="500">
  </a>
</div>

> **Video Guide:** You can run this entire project on your own computer. Detailed video instructions are available in [the YouTube video above](https://youtu.be/zG55QW73N0c).

---

## 📝 Development Article

**Behind the Scenes:** Read the detailed development journey and technical insights in this LinkedIn article:

👉 **Article:** [How the Train Seat Availability and the Train Seat Matrix Web Applications were Built](https://www.linkedin.com/pulse/bangladesh-railway-train-seat-availability-web-nishat-mahmud-u6hcc)

---

## 📚 Table of Contents

1. [Project Structure](#-project-structure)  
2. [Features Overview](#️-features-overview)  
3. [Authentication System](#-authentication-system)
4. [Core Logic](#-core-logic)  
5. [Matrix Algorithm](#-matrix-algorithm)  
6. [Frontend Features](#️-frontend-features)  
7. [Queue Management](#-queue-management)  
8. [API Integration](#-api-integration)  
9. [Cache Control](#-cache-control)  
10. [Technologies Used](#-technologies-used)  
11. [Setup Instructions](#-setup-instructions)  
12. [Configuration](#️-configuration)  
13. [License](#-license)

---

## 📂 Project Structure
```
.
├── app.py                        # Flask backend with routes, session mgmt & rendering
├── config.json                   # Dynamic config: maintenance, queue settings, app version
├── matrixCalculator.py           # Core matrix computation, API calls, fare calculations
├── request_queue.py              # Advanced queue system for managing concurrent requests
├── stations_en.json              # Complete list of Bangladesh Railway stations
├── trains_en.json                # Complete list of 120+ Bangladesh Railway trains
├── LICENSE                       # Project license
├── Procfile                      # Heroku/Render deployment configuration
├── README.md                     # Project documentation (this file)
├── requirements.txt              # Python dependencies
├── images/
│   ├── link_share_image.png      # Social sharing preview image
│   ├── Screenshot_1.png          # Interface screenshots
│   └── Screenshot_2.png          # Matrix view screenshots
├── static/
│   ├── css/
│   │   └── styles.css            # Responsive UI with matrix visualizations
│   ├── images/
│   │   ├── eid-al-adha-2025.png  # Event-specific banner image
│   │   └── sample_banner.png     # Default banner image
│   └── js/
│       └── script.js             # Frontend logic, validations, dropdowns
└── templates/
    ├── 404.html                  # Custom error page with auto-redirect
    ├── index.html                # Home form with train selection
    ├── matrix.html               # Seat matrix visualizer with route analysis
    ├── notice.html               # Maintenance mode page
    └── queue.html                # Queue status tracking page
```

---

## ⚙️ Features Overview

| Feature                                  | Status ✅ | Description |
|------------------------------------------|-----------|-------------|
| Segmented Seat Matrix Visualization      | ✅        | Complete route-to-route availability matrix |
| Direct & Segmented Route Finding         | ✅        | Smart algorithm for optimal ticket combinations |
| Mixed-Class Ticketing Analysis          | ✅        | Find routes using different seat classes |
| Real-time API Integration               | ✅        | Live data from Bangladesh Railway systems |
| Date-Aware Journey Planning             | ✅        | Handles overnight trains with proper segmentation |
| Interactive Availability Checker        | ✅        | Dynamic route analysis within matrix view |
| Advanced Queue Management               | ✅        | Prevents API overload with intelligent queuing |
| Responsive Matrix Tables                | ✅        | Mobile-optimized data visualization |
| Train Route Visualization              | ✅        | Complete route maps with timing information |
| Train Search by Route                  | ✅        | Collapsible interface for finding trains between stations |
| Maintenance Mode Support               | ✅        | Configurable site-wide notices |
| Session-based Form State              | ✅        | Preserves user input across requests |
| Custom Error Handling                 | ✅        | Graceful fallbacks for API failures |
| Social Media Integration              | ✅        | Open Graph tags for sharing |
| Cache-Control Headers                 | ✅        | Ensures fresh data on every request |
| User Activity Logging                 | ✅        | Comprehensive logging of user interactions and system events |
| JWT Authentication System             | ✅        | Automated Bearer token management and refresh |

---

## 🔐 Authentication System

### Smart Authentication Management

The application implements an intelligent JWT token system for accessing Bangladesh Railway APIs:

```python
def fetch_token() -> str
def set_token(token: str)
```

**Features:**
- **Automatic Token Refresh**: Detects expired tokens and refreshes automatically
- **Bearer Token Authentication**: Uses JWT tokens for all API requests
- **Secure Credential Management**: Environment-based configuration
- **Session Persistence**: Maintains authentication across requests
- **Error Recovery**: Handles invalid credentials gracefully
- **Rate Limit Handling**: Implements backoff strategies for API limits

### Environment Configuration

**Required Environment Variables:**
```bash
FIXED_MOBILE_NUMBER=your_mobile_number
FIXED_PASSWORD=your_password
```

### Token Lifecycle Management
- **Global Token Store**: Maintains active JWT token in memory
- **Timestamp Tracking**: Monitors token age and validity
- **Automatic Refresh**: Seamlessly renews expired tokens
- **Error Handling**: Graceful fallback for authentication failures

---

## 🧠 Core Logic

### 🚂 Train Matrix Computation

The heart of the application lies in `matrixCalculator.py`, which implements:

```python
def compute_matrix(train_model: str, journey_date_str: str, api_date_format: str) -> dict
```

**Process Flow:**
1. **Train Route Fetching**: Gets complete route with all stations and timings
2. **Parallel API Calls**: Uses ThreadPoolExecutor for concurrent seat availability checks
3. **Matrix Construction**: Builds N×N matrix for all station-to-station combinations
4. **Fare Aggregation**: Processes multiple seat classes (S_CHAIR, SNIGDHA, AC_B, etc.)

### 🔄 Smart Route Finding Algorithm

Three intelligent routing strategies:

#### 1. Direct Routes
```javascript
// Checks for direct tickets between origin and destination
const directRoute = fareMatrices[seatType][origin][destination];
```

#### 2. Segmented Routes (Same Class)
```javascript
// Finds optimal path through intermediate stations
function findRoutes(origin, destination, seatType, stations, fareMatrices)
```

#### 3. Mixed-Class Routes
```javascript
// Uses different seat classes for different segments
function findMixedRoutes(origin, destination, stations, fareMatrices, seatTypes)
```

### 📊 Seat Type Processing

Supports all Bangladesh Railway seat classes:
- **S_CHAIR** (Shovan Chair)
- **SHOVAN** (Shovan)
- **SNIGDHA** (Snigdha)
- **F_SEAT** (First Class Seat)
- **F_CHAIR** (First Class Chair)
- **AC_S** (AC Seat)
- **F_BERTH** (First Class Berth)
- **AC_B** (AC Berth)
- **SHULOV** (Shulov)
- **AC_CHAIR** (AC Chair)

---

## 🧮 Matrix Algorithm

### Data Structure
```python
fare_matrices = {
    "seat_type": {
        "from_station": {
            "to_station": {
                "online": int,     # Available seats
                "offline": int,    # Counter seats
                "fare": float,     # Base fare
                "vat_amount": float # VAT amount
            }
        }
    }
}
```

### Concurrent Processing
- **ThreadPoolExecutor**: Parallel API calls for all route segments
- **Max Workers**: Dynamically calculated based on route complexity
- **Timeout Handling**: 30-second timeout per API call
- **Error Recovery**: Graceful handling of failed requests

### Matrix Visualization
- **Color-coded Cells**: Available (green), unavailable (gray), disabled (diagonal)
- **Fare Display**: Shows total fare including VAT and charges
- **Direct Links**: Click-to-buy integration with official booking system
- **Responsive Design**: Horizontal scroll on mobile devices

---

## 🎨 Frontend Features

### 1. Advanced Train Selection
- **Autocomplete Dropdown**: 120+ trains with fuzzy search
- **Model Extraction**: Automatically extracts train numbers from names
- **Validation**: Ensures valid train selection before submission
- **Train Search by Route**: Collapsible section for finding trains between specific stations

### 2. Matrix Interaction
- **Expandable Route View**: Collapsible train route with station timings
- **Availability Checker**: Interactive origin/destination selector within matrix
- **Real-time Calculations**: Dynamic fare computation for route segments

### 3. Train Search Feature
- **Collapsible Interface**: Expandable section for route-based train search
- **Station Autocomplete**: Smart dropdown with station name suggestions
- **Bidirectional Search**: Swap origin/destination with single click
- **Live Train Discovery**: Real-time API calls to find available trains
- **Click-to-Select**: Direct integration with main train selection field

### 3. Mobile Optimization
- **Responsive Tables**: Horizontal scroll with sticky headers
- **Touch-friendly Controls**: Large tap targets for mobile interaction
- **Optimized Layout**: Single-column layout on small screens

### 4. Date Intelligence
```javascript
// Handles overnight journeys with proper date calculation
const hasSegmentedDates = stations.some(station => 
    stationDates[station] !== date
);
```

### 5. Train Discovery System
```javascript
// API endpoint for finding trains between stations
const response = await fetch('/search_trains', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ origin: origin, destination: destination })
});
```

---

## ⏳ Queue Management

### Advanced Request Queue (`request_queue.py`)

**Features:**
- **Concurrent Limiting**: Configurable max concurrent requests
- **Cooldown Periods**: Prevents API flooding
- **Request Prioritization**: FIFO with abandonment detection
- **Health Monitoring**: Tracks processing times and success rates
- **Auto-cleanup**: Removes stale requests and results

**Configuration:**
```json
{
    "queue_max_concurrent": 1,
    "queue_cooldown_period": 3,
    "queue_batch_cleanup_threshold": 10,
    "queue_cleanup_interval": 30,
    "queue_heartbeat_timeout": 60
}
```

**Process Flow:**
1. Request submitted → Added to queue
2. Queue position displayed to user
3. Request processed when slot available
4. Results cached and delivered
5. Automatic cleanup of completed requests

---

## 🔌 API Integration

### Bangladesh Railway API Endpoints

#### 1. Authentication
```http
POST https://railspaapi.shohoz.com/v1.0/web/auth/sign-in
Content-Type: application/json
{
    "mobile_number": "MOBILE_NUMBER",
    "password": "PASSWORD"
}
```

#### 2. Train Route Data
```http
POST https://railspaapi.shohoz.com/v1.0/web/train-routes
Content-Type: application/json
{
    "model": "TRAIN_MODEL",
    "departure_date_time": "YYYY-MM-DD"
}
```

#### 3. Seat Availability
```http
GET https://railspaapi.shohoz.com/v1.0/web/bookings/search-trips-v2
Headers: Authorization: Bearer {jwt_token}
Params: from_city, to_city, date_of_journey, seat_class
```

#### 3. Train Search Between Stations
```http
POST /search_trains
Headers: Authorization: Bearer {jwt_token}
Content-Type: application/json
{
    "origin": "STATION_NAME",
    "destination": "STATION_NAME"
}
```

### Error Handling
- **Network Timeouts**: 30-second request timeout
- **Rate Limiting**: Built-in cooldown mechanisms with 403 error detection
- **Authentication Refresh**: Automatic JWT token renewal on expiration
- **Credential Validation**: Environment variable validation and secure error messaging
- **Fallback Responses**: Graceful degradation on API failures
- **Retry Logic**: Automatic retries for transient failures

---

## 🚦 Cache Control

All responses include strict cache headers:
```http
Cache-Control: no-store, no-cache, must-revalidate, max-age=0
Pragma: no-cache
Expires: 0
```

**Benefits:**
- Always fresh data from APIs
- No stale seat availability information
- Proper handling of dynamic content
- Prevents browser caching issues

---

## 🧰 Technologies Used

### Backend
- **Python 3.10+**
- **Flask 3.1.0** - Web framework
- **requests 2.32.3** - HTTP client for API calls
- **pytz 2025.2** - Timezone handling for BST
- **python-dotenv** - Environment variable management for secure authentication
- **colorama 0.4.6** - Terminal color output
- **gunicorn 23.0.0** - WSGI server for production deployment
- **Structured Logging** - INFO level logging with timestamp and user activity tracking

### Frontend
- **HTML5** with semantic markup
- **CSS3** with Flexbox and Grid
- **Vanilla JavaScript** - No external dependencies
- **Font Awesome 6.5.0** - Icon library
- **Responsive Design** - Mobile-first approach

### Data Processing
- **Concurrent Programming** - ThreadPoolExecutor
- **JSON Processing** - Native Python JSON
- **Date/Time Handling** - pytz for timezone awareness
- **Matrix Algorithms** - Custom pathfinding implementation

---

## 🧪 Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/nishatrhythm/Bangladesh-Railway-Train-Seat-Matrix-Web-Application.git
cd Bangladesh-Railway-Train-Seat-Matrix-Web-Application
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file or set environment variables for Bangladesh Railway API authentication:
```bash
FIXED_MOBILE_NUMBER=your_mobile_number
FIXED_PASSWORD=your_password
```

### 4. Configure Application
Edit `config.json` for customization:
```json
{
    "version": "1.0.0",
    "is_maintenance": 0,
    "queue_max_concurrent": 1,
    "queue_cooldown_period": 3,
    "queue_enabled": true
}
```

### 5. Run Application
```bash
python app.py
```

**Production Deployment:**
```bash
# With Gunicorn (recommended for production)
gunicorn app:app --log-level=info --access-logfile=-
```

**Logging Output:**
The application will display structured logs including:
- Timestamp and log level
- User submissions with device/browser information
- API request details and response status
- Queue management and processing events
- Error tracking and system health monitoring

### 6. Access Application
Visit `http://localhost:5000` in your browser

---

## ⚙️ Configuration

### Authentication Configuration
Environment variables for Bangladesh Railway API access:
```bash
FIXED_MOBILE_NUMBER=your_mobile_number  # Required for JWT token authentication
FIXED_PASSWORD=your_password            # Required for JWT token authentication
```

**Security Notes:**
- Never commit credentials to version control
- Use environment variables or secure secret management
- Credentials are loaded from `/etc/secrets/.env` in production environments

### Queue Settings
- **max_concurrent**: Number of simultaneous API requests (default: 1)
- **cooldown_period**: Delay between requests in seconds (default: 3)
- **batch_cleanup_threshold**: Trigger cleanup after N completed requests
- **cleanup_interval**: Background cleanup frequency in seconds
- **heartbeat_timeout**: Request timeout in seconds

### Maintenance Mode
```json
{
    "is_maintenance": 1,
    "maintenance_message": "Site is under maintenance..."
}
```

### Banner System
```json
{
    "is_banner_enabled": 1,
    "image_link": "https://example.com/banner.png",
    "force_banner": 0
}
```

---

## 🔧 API Response Format

### Matrix Data Structure
```json
{
    "stations": ["DHAKA", "CHATTOGRAM", "SYLHET"],
    "fare_matrices": {
        "S_CHAIR": {
            "DHAKA": {
                "CHATTOGRAM": {
                    "online": 45,
                    "offline": 12,
                    "fare": 350.0,
                    "vat_amount": 0.0
                }
            }
        }
    },
    "station_dates": {
        "DHAKA": "2025-05-26",
        "CHATTOGRAM": "2025-05-26"
    }
}
```

### User Activity Logging

The application implements comprehensive logging to track user interactions and system performance:

**Logging Configuration:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
```

**Logged Events:**
- **Train Matrix Requests**: `Train Matrix Request - Train: 'TRAIN_NAME', Date: 'DATE' | Device: TYPE, Browser: BROWSER`
- **Train Search Requests**: `Train Search Request - From: 'ORIGIN', To: 'DESTINATION' | Device: TYPE, Browser: BROWSER`
- **System Events**: Queue status, API failures, and error handling
- **Production Logs**: Gunicorn access logs with `--log-level=info --access-logfile=-`

**Device & Browser Detection:**
- Automatically detects user device type (Mobile/PC)
- Identifies browser (Chrome, Firefox, Safari, Edge, Opera, IE)
- Logs user agent information for analytics and debugging

---

## 🛡️ Security Features

- **Input Sanitization**: All form inputs validated server-side
- **Session Management**: Secure session handling with Flask
- **XSS Protection**: Proper template escaping
- **CSRF Protection**: Session-based form validation
- **Rate Limiting**: Queue system prevents API abuse

---

## 📱 Mobile Features

- **Responsive Tables**: Horizontal scroll with fixed headers
- **Touch Optimization**: Large clickable areas
- **Adaptive Layout**: Single-column on mobile
- **Fast Loading**: Optimized assets and lazy loading
- **Offline Detection**: Network status awareness

---

## 🎯 Future Enhancements

- [ ] Multi-language support (Bengali/English)
- [ ] API caching layer for improved performance

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## ⚖️ Disclaimer

This application uses **publicly accessible APIs** provided by Bangladesh Railway's official e-ticketing platform. All data is fetched through legitimate REST endpoints without any reverse engineering or unauthorized access.

- **Educational Purpose**: Designed for learning and informational use
- **API Compliance**: Respects rate limits and terms of service
- **No Data Scraping**: Uses official API endpoints only
- **Privacy Focused**: No user data collection or storage

If requested by the official service provider, access will be adjusted accordingly.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Bangladesh Railway** for providing public API access
- **Shohoz** for the e-ticketing platform integration
- **Open Source Community** for inspiration and tools
- **Contributors** who help improve this project

---

<div align="center">

**Made with ❤️ for Bangladesh Railway passengers**

[🌐 Live Demo](https://seat.onrender.com) | [📧 Feedback](https://forms.gle/NV72PC1z75sq77tg7) | [⭐ Star on GitHub](https://github.com/nishatrhythm/Bangladesh-Railway-Train-Seat-Matrix-Web-Application)

</div>

## Deploying on Render

To deploy this application on [Render](https://render.com/):

1. **Push your code to a Git repository** (GitHub, GitLab, or Bitbucket).
2. **Create a new Web Service** on Render and connect your repository.
3. **Set the build and start commands:**
   - **Build Command:** (leave blank for Python projects)
   - **Start Command:** `gunicorn app:app --log-level=info --access-logfile=-`
4. **Add environment variables** in the Render dashboard:
   - `FIXED_MOBILE_NUMBER` (your mobile number)
   - `FIXED_PASSWORD` (your password)
5. **Ensure the following files are present in your repo:**
   - `requirements.txt`
   - `Procfile`
   - `.env.example` (for reference, do not include real secrets)
6. **Deploy!** Render will build and start your app. You will get a public URL when it is live.

For more details, see the official [Render Python deployment guide](https://render.com/docs/deploy-python).