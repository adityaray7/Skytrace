# SkyTrace - Satellite Imagery Timeline Explorer

SkyTrace is a web application that allows users to explore satellite imagery over time. Select any point on the globe and instantly view a historical timeline of Sentinel-2 satellite images, streamed directly from Google Earth Engine.

## Tech Stack

- **Frontend**: 
  - [React](https://reactjs.org/)
  - [Google Maps JavaScript API](https://developers.google.com/maps/documentation/javascript)
  - CSS3

- **Backend**:
  - [FastAPI](https://fastapi.tiangolo.com/) (Python 3)
  - [Google Earth Engine API](https://earthengine.google.com/)
  - [Uvicorn](https://www.uvicorn.org/)

## Getting Started

Follow these instructions to get the project running on your local machine.

### Prerequisites

- [Node.js](https://nodejs.org/en/) (v14 or later)
- [Python](https://www.python.org/downloads/) (v3.8 or later) and `pip`
- A Google Account for Earth Engine authentication.
- A Google Cloud Platform project with the **Maps JavaScript API** enabled to get an API key.

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd skytrace/backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Authenticate with Google Earth Engine:**
    Run the following command and follow the prompts to log in with your Google account.
    ```bash
    earthengine authenticate
    ```

5.  **Run the server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The backend will be running at `http://127.0.0.1:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd ../frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Set up environment variables:**
    Copy the example environment file:
    ```bash
    cp .env.example .env.local
    ```
    Now, open `.env.local` and add your Google Maps API key:
    ```
    REACT_APP_GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY_HERE
    ```

4.  **Start the application:**
    ```bash
    npm start
    ```
    The frontend will open and run at `http://localhost:3000`.



## GCP Setup

To run and deploy this project, you need to enable the following APIs in your Google Cloud project:

- **Maps JavaScript API**: For the interactive map.
- **Earth Engine API**: For querying satellite imagery.
- **Cloud Run API**: For deploying the backend service.
- **Artifact Registry API**: For storing the backend Docker image.
- **Cloud Firestore API**: For metadata caching (future).
- **Secret Manager API**: For securely managing API keys.

---

## Architecture

- **Frontend**: React/Next.js with Google Maps/Leaflet
- **Backend**: Python (FastAPI) on Cloud Run
- **Data Source**: Google Earth Engine & Sentinel Hub
- **Caching**: Firestore
- **Hosting**: Firebase Hosting
