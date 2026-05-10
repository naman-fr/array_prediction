# Sentinel AI: Radar Array Spacing Predictor 🛰️

A production-grade, Agentic AI platform for optimizing element spacing in 4-element radar arrays to achieve target angular accuracy.

## 🌟 Features

- **Agentic AI Interface**: Natural language configuration via our embedded conversational assistant.
- **Deep Learning Model**: High-performance multi-layer perceptron mapping target RMS angular error to optimal array spacings.
- **Robust Physics Engine**: Multi-frequency CRT Unwrapping for resolving phase ambiguities.
- **Microservice Backend**: Scalable FastAPI service exposing endpoints for prediction, simulation, and conversational logic.
- **Next.js & Three.js Frontend**: Immersive, glassmorphism-styled dashboard with real-time 3D array visualizations.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+

### Setup the AI Backend

```bash
cd backend
python -m venv venv
# Activate venv:
# Windows: venv\Scripts\activate
# Unix: source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```
The backend will run on `http://localhost:8000`.

### Setup the Next.js Frontend

```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser to interact with the Sentinel AI dashboard.

## 🧠 Architecture

### `backend/`
- `ml/dataset.py`: Physics simulation and dataset generator.
- `ml/model.py`: MLP Keras model architecture and training loops.
- `ml/inference.py`: Model inference wrapper with CRT boundary enforcement.
- `agent.py`: Conversational logic layer parsing natural language to model endpoints.
- `main.py`: FastAPI server.

### `frontend/`
- Next.js 14 App Router
- React Three Fiber for 3D visualizations
- Tailwind CSS with custom glassmorphism tokens
- Lucide React for consistent iconography

## 🎯 Use Cases

1. **Defense & Aerospace**: Rapidly prototype radar array geometries.
2. **Research**: Analyze CRT unwrapping and boundary constraints.
3. **Education**: Interactive learning of phase arrays and machine learning integrations.

## 🤝 Contributing

Contributions are welcome. Please ensure your commits follow conventional commit formats.

## 📄 License

MIT License