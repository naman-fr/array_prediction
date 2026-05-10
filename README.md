# Sentinel AI: Radar Array Spacing Predictor 🛰️

A production-grade, Agentic AI platform for optimizing element spacing in 4-element radar arrays to achieve target angular accuracy.

## 🌟 Features

- **ReAct Agentic AI Interface**: Advanced reasoning-based conversational assistant with modular tool-calling and stateful session memory.
- **Deep Learning Model**: High-performance multi-layer perceptron mapping target RMS angular error to optimal array spacings.
- **Robust Physics Engine**: Multi-frequency Hierarchical Robust CRT Unwrapping and CRLB (Cramer-Rao Lower Bound) theoretical benchmarking.
- **Digital Twin 3D Dashboard**: Immersive Next.js & Three.js interface with interactive 3D tooltips, radome rendering, and real-time radiation pattern (Array Factor) plotting.
- **MLOps & Observability**: Asynchronous background retraining pipeline and integrated Prometheus metrics for real-time monitoring.
- **Enterprise Architecture**: Domain-driven FastAPI routers and SQLAlchemy-backed SQLite persistence for conversational state.

## 🚀 Quick Start

### Docker (Recommended)

You can spin up both the FastAPI backend and Next.js frontend simultaneously using Docker Compose:

```bash
docker-compose up --build
```
- Backend API is accessible at `http://localhost:8000`
- Frontend Dashboard is accessible at `http://localhost:3000`

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
# Activate venv:
# Windows: venv\Scripts\activate
# Unix: source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🧪 Testing

We use `pytest` for robust mathematical and API testing.

```bash
cd backend
pytest tests/
```

## 🧠 Architecture

### `backend/`
- `api/`: Domain-driven routers for ML, Chat, and Hardware (HIL).
- `db/`: Persistence layer using SQLAlchemy and SQLite.
- `ml/`: Core physics simulation, model training, and pattern analysis.
- `ml/pattern.py`: Array Factor (Radiation Pattern) computation.
- `ml/crlb.py`: Cramer-Rao Lower Bound analytical benchmarking.
- `agent.py`: ReAct-based agent executor with tool-calling registry.
- `main.py`: FastAPI server entry point with Prometheus instrumentation.
- `hil_mock.py`: Hardware-in-the-loop mock service for SCPI deployment.

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