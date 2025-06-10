# Radar Array Spacing Predictor 🛰️

A machine learning-based tool for optimizing element spacing in 4-element radar arrays to achieve target angular accuracy.

![Radar Array Visualization](docs/radar-visualization.png)

## 🌟 Features

- **ML-Based Spacing Prediction**: Neural network model predicts optimal element spacings for target RMS angular error
- **Multi-Frequency CRT Unwrapping**: Robust phase unwrapping using Chinese Remainder Theorem
- **Interactive 3D Visualization**: Real-time visualization of array geometry and radiation patterns
- **FastAPI Backend**: High-performance API for predictions and model management
- **Next.js Frontend**: Modern, responsive UI with real-time updates

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Node.js 14+
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/naman-fr/array_prediction.git
cd array_prediction
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd ../frontend
npm install
```

### Running the Application

1. Start the backend server:
```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
uvicorn main:app --reload
```

2. In a new terminal, start the frontend:
```bash
cd frontend
npm run dev
```

3. Open your browser and navigate to `http://localhost:3000`

## 📊 Technical Details

### Backend Architecture

- **FastAPI**: High-performance API framework
- **TensorFlow**: ML model for spacing prediction
- **NumPy/SciPy**: Scientific computing and optimization
- **CRT Algorithm**: Multi-frequency phase unwrapping

### Frontend Architecture

- **Next.js**: React framework with SSR
- **Three.js**: 3D visualization
- **Tailwind CSS**: Styling
- **TypeScript**: Type-safe development

### ML Model

- **Architecture**: Multi-layer perceptron (MLP)
- **Input**: Target RMS angular error
- **Output**: Optimal element spacings [d1, d2, d3]
- **Training**: Synthetic dataset with realistic phase noise

## 📝 API Documentation

### Endpoints

- `POST /predict`: Get optimal spacings for target error
- `GET /model/info`: Get model metadata
- `POST /verify`: Verify achieved error for given spacings

### Example Request

```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={"target_error": 0.1}  # degrees
)
spacings = response.json()["spacings"]
```

## 🎯 Use Cases

1. **Radar Array Design**: Optimize element spacing for desired angular accuracy
2. **Educational Tool**: Learn about array design and phase unwrapping
3. **Research**: Study the relationship between spacing and angular accuracy

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

- **Naman** - [GitHub](https://github.com/naman-fr)

## 🙏 Acknowledgments

- TensorFlow team for the ML framework
- FastAPI for the backend framework
- Three.js for 3D visualization
- Next.js team for the frontend framework 