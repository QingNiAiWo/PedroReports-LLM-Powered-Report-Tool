# 🦝 PedroReports
> Your Pawsome Reporter 🐾

[![License](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-Latest-61dafb.svg)](https://reactjs.org)
[![Vite](https://img.shields.io/badge/Vite-Latest-646cff.svg)](https://vitejs.dev)

## What is PedroReports?

<iframe width="560" height="315" src="https://youtu.be/DFu0m22gfe8" frameborder="0" allowfullscreen></iframe>

PedroReports is your clever companion for data analysis, transforming raw datasets into polished insights through the power of Google's Gemini AI. With a curious eye and quick thinking, it turns your CSV datasets into comprehensive, professional PDF reports with minimal effort. Whether you're analyzing financial trends, healthcare metrics, marketing data, or any other tabular dataset, PedroReports is ready to dig through your data and uncover hidden treasures.

Simply upload your data, ask your questions naturally, and let PedroReports:

- 🤖 Process your data using advanced AI analysis
- 📊 Create beautiful, informative visualizations
- 📝 Perform detailed statistical analysis
- 📑 Generate polished PDF reports automatically
- 💡 Deliver AI-powered insights and recommendations

### Industry Applications

PedroReports excels across various domains:

- 📈 **Finance**: Analyze market trends, investment portfolios, and financial statements
- 🏥 **Healthcare**: Process patient data, treatment outcomes, and clinical trials
- 📊 **Business Analytics**: Track KPIs, sales metrics, and customer behavior
- 📱 **Marketing**: Evaluate campaign performance and customer engagement
- 🔬 **Research**: Analyze experimental data and survey responses
- 📦 **Supply Chain**: Monitor inventory levels and logistics metrics

## Features

- 📊 Automated data analysis and visualization
- 📝 AI-powered insights generation using Google's Gemini model
- 📈 Interactive data visualizations with Recharts
- 📱 Responsive and modern UI with Tailwind CSS
- 🎨 Light/Dark mode support
- 🔒 Secure file handling and validation
- 📄 Professional PDF report generation
- 🚀 Real-time processing status updates

## Tech Stack

### Frontend
- ⚛️ React with Vite for blazing-fast development
- 🎨 Tailwind CSS for styling
- 📊 Recharts for data visualization
- 🌓 Custom theming system
- 🔧 Modern React Hooks and best practices

### Backend
- ⚡ FastAPI for high-performance API
- 🤖 Google Gemini AI for intelligent analysis
- 🔗 Langchain for AI orchestration and prompt management
- 📊 Pandas & NumPy for data processing
- 📈 Matplotlib & Seaborn for visualization
- 📑 ReportLab for PDF generation

## Getting Started

### Prerequisites
- Node.js 16+ 📦
- Python 3.11+ 🐍
- pip 🔧
- Virtual environment (recommended) 🌐

### Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/bobinsingh/PedroReports.git
cd pedroreports
```

2. **Backend Setup**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Rename .env.example to .env and add your API key
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Start Development Servers**

Backend:
```bash
# From root directory
uvicorn main:app --reload --port 8000
```

Frontend:
```bash
# From frontend directory
npm run dev
```

Visit `http://localhost:5173` to access the application 🌐

## Features in Detail

### Data Analysis
- 📊 Automated statistical analysis
- 📈 Trend detection and pattern recognition
- 🔍 Outlier detection
- 📉 Correlation analysis
- 📊 Distribution analysis

### Visualization
- 📊 Dynamic chart generation
- 📈 Interactive data exploration
- 🎨 Customizable visual themes
- 📱 Responsive design
- 📊 Multiple chart types support

### Report Generation
- 📄 Professional PDF reports
- 📝 AI-generated insights
- 📊 Embedded visualizations
- 📑 Executive summaries
- 🔍 Detailed analysis sections

## Project Structure

```
project/
├── backend/           # FastAPI backend
│   ├── api/          # API endpoints
│   ├── core/         # Core functionality
│   ├── services/     # Key Components
│   └── domain/       # Domain models
│
└── frontend/         # React frontend
    ├── src/
    │   ├── components/   # React components
    │   ├── styles/       # CSS styles
    │   └── App.jsx      # Main application
    └── public/          # Static assets
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI for the amazing backend framework
- React team for the frontend library
- Google for the Gemini AI model
- Langchain for AI orchestration capabilities
- All contributors and supporters

---
Crafted with 🦝 by Bobin Singh
