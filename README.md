# AI Fog & Night Vision System

> **Real-Time Computer Vision for Adaptive Visibility Enhancement**

A real-time video enhancement platform designed to improve visual clarity across challenging environmental conditions such as **fog, low-light scenes, and reduced-contrast environments**.

The system combines a responsive React interface with a Python-based computer vision engine, enabling users to upload video, select an enhancement mode, tune visual parameters, and observe the processed output as a continuous real-time stream.

---

## 1. Project Overview

Visibility is a fundamental challenge for vision-based systems operating in changing environmental conditions. A scene that is clear under normal illumination can become significantly harder to interpret when affected by fog, darkness, or poor contrast.

This project explores a lightweight approach to that problem by building an **interactive visibility-enhancement pipeline** capable of processing video frames continuously and adapting the output according to the selected operating mode.

The system brings together:

* Real-time frame processing
* Adaptive contrast enhancement
* Low-light visualization
* Edge-based scene highlighting
* Interactive parameter control
* Continuous video streaming
* A modular frontend/backend architecture

The result is a compact computer-vision platform that demonstrates how image-processing algorithms can be combined into a practical, interactive vision system.

---

## 2. Key Capabilities

### 2.1 Adaptive Fog Enhancement

Enhances local image contrast to make structures and visual details more distinguishable in scenes affected by atmospheric visibility degradation.

The implementation works in the **LAB color space**, applying CLAHE to the luminance component while maintaining the image's color information.

### 2.2 Night Vision

Transforms low-light imagery into a high-visibility visualization by combining:

* Grayscale conversion
* Dynamic brightness adjustment
* Contrast enhancement
* CLAHE-based local enhancement
* Green-channel visualization

This produces a night-vision-inspired representation designed to emphasize useful scene information.

### 2.3 Interactive Visual Controls

The interface exposes configurable parameters including:

* Processing mode
* Fog enhancement strength
* Brightness
* Contrast
* Split-screen comparison
* Edge highlighting

These settings can be updated dynamically through the backend API.

### 2.4 Edge Highlighting

An optional edge-analysis layer uses **Canny edge detection** to identify prominent boundaries within the scene.

Detected edges can be overlaid onto the processed frame, providing an additional visual representation of scene structure.

### 2.5 Real-Time Video Pipeline

Uploaded videos are processed frame-by-frame and delivered to the frontend through a continuous **MJPEG stream**.

The processing loop is designed around a target of approximately 30 FPS, with computational considerations built into the pipeline.

---

## 3. System Architecture

```text
                         USER
                          │
                          ▼
                ┌──────────────────┐
                │   React + Vite   │
                │    Frontend      │
                └────────┬─────────┘
                         │
                    HTTP / API
                         │
                         ▼
                ┌──────────────────┐
                │     FastAPI      │
                │     Backend      │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ VisionProcessor  │
                │     OpenCV       │
                └────────┬─────────┘
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
          Normal       Fog         Night
             │           │           │
             │         CLAHE      Enhancement
             │           │           │
             └───────────┼───────────┘
                         │
                         ▼
                  Edge Highlighting
                     (Optional)
                         │
                         ▼
                  JPEG Encoding
                         │
                         ▼
                 MJPEG Video Stream
                         │
                         ▼
                ┌──────────────────┐
                │   React Display  │
                └──────────────────┘
```

---

## 4. Processing Pipeline

Each video frame follows a consistent processing pipeline:

```text
Video Input
     ↓
Frame Extraction
     ↓
Resize to 640 × 480
     ↓
Selected Enhancement Mode
     ↓
Brightness / Contrast Adjustment
     ↓
Optional Edge Highlighting
     ↓
JPEG Encoding
     ↓
MJPEG Streaming
     ↓
Frontend Visualization
```

This architecture separates **video acquisition, image processing, API communication, and presentation**, making the system easier to maintain and extend.

---

## 5. Computer Vision Engine

The core processing engine is implemented through the `VisionProcessor` class.

It maintains the current processing state and provides dedicated operations for different visibility conditions.

### 5.1 CLAHE Enhancement

CLAHE — **Contrast Limited Adaptive Histogram Equalization** — is used to improve local contrast.

The fog-processing pipeline is:

```text
BGR Image
    ↓
LAB Color Space
    ↓
Separate Luminance Channel
    ↓
CLAHE
    ↓
Merge LAB Channels
    ↓
BGR Image
```

The enhancement strength can be dynamically influenced through the application's fog-strength parameter.

### 5.2 Night Enhancement

The night-vision pipeline is:

```text
Color Frame
     ↓
Grayscale
     ↓
Brightness / Contrast Scaling
     ↓
CLAHE
     ↓
Green-Channel Visualization
     ↓
Enhanced Night Frame
```

This approach emphasizes intensity variations and scene details while producing a recognizable night-vision visualization.

### 5.3 Edge Analysis

When enabled:

```text
Enhanced Frame
      ↓
Grayscale Conversion
      ↓
Canny Edge Detection
      ↓
Edge Mask
      ↓
Overlay on Frame
```

This provides an additional structural representation of the scene.

---

## 6. Performance-Oriented Design

Real-time computer vision requires a balance between **visual quality and computational cost**.

Several design decisions were made specifically around that constraint.

### 6.1 Frame Resolution

Frames are resized to:

```text
640 × 480
```

before intensive processing.

This reduces the number of pixels processed per frame and helps maintain responsiveness.

### 6.2 Controlled Processing Rate

The streaming loop introduces a small delay and targets approximately:

```text
~30 FPS maximum
```

This prevents unnecessary CPU saturation while maintaining a responsive video experience.

### 6.3 Asynchronous Backend

FastAPI handles the HTTP layer asynchronously.

Synchronous OpenCV processing is moved into a background thread using AnyIO, preventing intensive frame processing from blocking the asynchronous event loop.

### 6.4 Reusable CLAHE Processor

CLAHE is initialized as part of the vision processor and reused during frame processing rather than unnecessarily constructing a new processor for every frame.

---

## 7. Backend API

The FastAPI backend exposes a focused set of endpoints.

| Endpoint        | Method | Purpose                              |
| --------------- | ------ | ------------------------------------ |
| `/upload_video` | POST   | Upload and initialize a video source |
| `/video_feed`   | GET    | Stream processed frames              |
| `/api/settings` | GET    | Retrieve current processing settings |
| `/api/settings` | POST   | Update processing parameters         |

### 7.1 Configurable Parameters

The backend supports configuration for:

```text
Mode
Fog Strength
Brightness
Contrast
Split Screen
Edge Highlighting
```

This makes the vision engine controllable independently from the frontend implementation.

---

## 8. Frontend

The user interface is built with **React and Vite**.

The frontend provides the interaction layer for the vision system, allowing users to:

1. Upload a video.
2. Select a visibility mode.
3. Adjust enhancement parameters.
4. Enable visual analysis features.
5. Observe the processed output.

Vite provides the development and build environment, while React manages the interactive interface.

---

## 9. Project Structure

```text
AI_Fog_Night_Vision_System/
│
├── backend/
│   ├── main.py
│   ├── vision.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   │
│   ├── public/
│   │
│   └── src/
│       ├── App.jsx
│       ├── app.css
│       ├── index.css
│       ├── main.jsx
│       └── assets/
│
├── .gitignore
└── README.md
```

---

## 10. Technology Stack

| Layer                | Technology      |
| -------------------- | --------------- |
| Frontend             | React           |
| Build Tool           | Vite            |
| Backend              | FastAPI         |
| Server               | Uvicorn         |
| Computer Vision      | OpenCV          |
| Numerical Processing | NumPy           |
| Data Validation      | Pydantic        |
| Async Processing     | AnyIO / asyncio |
| Video Streaming      | MJPEG           |

---

## 11. Getting Started

### 11.1 Prerequisites

Install:

* Python 3
* Node.js
* npm

### 11.2 Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI_Fog_Night_Vision_System.git
cd AI_Fog_Night_Vision_System
```

### 11.3 Start the Backend

```bash
cd backend
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the server:

```bash
python main.py
```

The backend runs on:

```text
http://127.0.0.1:8080
```

### 11.4 Start the Frontend

Open a second terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL displayed by Vite.

---

## 12. Engineering Principles

The project was designed around several practical engineering principles.

### 12.1 Modularity

The frontend, API layer, and vision-processing engine are separated into distinct components.

### 12.2 Real-Time Responsiveness

Processing decisions prioritize responsiveness and predictable execution while maintaining useful visual enhancement.

### 12.3 Parameterization

Enhancement behavior is exposed through configurable parameters rather than hard-coded visual settings.

### 12.4 Extensibility

The `VisionProcessor` architecture makes it straightforward to introduce additional processing modes and computer-vision algorithms.

### 12.5 Hardware Awareness

Resolution control, reusable processing objects, and background execution help keep the system practical on machines with limited computational resources.

---

## 13. Applications

The system can serve as a foundation for:

* Driver-assistance interfaces
* Visibility enhancement systems
* Automotive computer vision
* Low-light video enhancement
* Foggy-environment visualization
* Computer vision experimentation
* Real-time vision interfaces

The architecture also provides a starting point for integrating more advanced perception capabilities in future iterations.

---

## 14. Future Development

The modular architecture provides a foundation for expanding the platform with capabilities such as:

* Live camera input
* GPU-accelerated processing
* Advanced image dehazing
* Learned low-light enhancement
* Lane detection
* Object detection
* Vehicle and pedestrian recognition
* Temporal video enhancement
* Real-time performance monitoring
* Edge-device deployment
* Integration with automotive perception systems

---

## 15. Project Vision

The broader objective of the project is to explore how **real-time computer vision can transform raw visual input into more interpretable information under difficult environmental conditions**.

Rather than treating visibility enhancement as a single image filter, the system approaches it as an interactive pipeline where **processing mode, enhancement parameters, scene structure, and real-time constraints** work together.

This creates a foundation that can evolve from a visualization system into a broader real-time perception platform.

---

## 16. Built With

**React · Vite · FastAPI · Python · OpenCV · NumPy**
