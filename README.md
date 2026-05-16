<div align="center">
  <img src="https://img.icons8.com/color/144/000000/diabetes.png" alt="InSight Logo" width="120" />
  <h1>InSight: AI-Powered Glycemic Load Estimator</h1>
  <p><em>Real-time Dietary Awareness & Insulin Guidance System via 3D Computer Vision and RAG</em></p>

  [![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev/)
  [![Spring Boot](https://img.shields.io/badge/Spring_Boot-F2F4F9?style=for-the-badge&logo=spring-boot)](https://spring.io/projects/spring-boot)
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Java 17](https://img.shields.io/badge/Java_17-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)](https://openjdk.java.net/)
  [![Milvus](https://img.shields.io/badge/Milvus-0A2040?style=for-the-badge&logo=milvus&logoColor=white)](https://milvus.io/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
</div>

---

## 📖 Table of Contents
- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Methodology & Safety](#-methodology--safety)
- [Acknowledgments](#-acknowledgments)

---

## 💡 About the Project

**InSight** is an advanced Proof-of-Concept (PoC) dietary awareness tool designed for diabetic patients. It leverages monocular depth estimation (**Depth Anything V2**) and object detection (**YOLOv8**) to estimate food volume and calculates the **Glycemic Load (GL)**. Furthermore, it integrates a **Retrieval-Augmented Generation (RAG)** service backed by a Milvus vector database and the Gemini API to provide context-aware, personalized dietary advice and insulin dosing recommendations based on ADA clinical guidelines.

> **Disclaimer:** InSight is a research prototype intended for educational and dietary awareness purposes. It is **not** a substitute for professional medical advice, diagnosis, or treatment.

---

## ✨ Key Features

- 📸 **Automated GL Estimation:** Simply take a top-down photo of your meal. The system estimates volume, identifies the food, and calculates Glycemic Load in real-time.
- 🧠 **Context-Aware RAG Chatbot:** Ask questions about your diet. The chatbot is grounded in verified medical documents (ADA & WHO guidelines) using Milvus and Gemini to prevent hallucinations.
- 🛡️ **3-Layer Medical Safety:**
  1. *Prompt Guardrails:* LLM is strictly prohibited from directly prescribing dosages.
  2. *Grounding Validator:* Rejects LLM outputs if they deviate >20% from hard-coded Python rule-based calculations.
  3. *Hard Cap Limits:* Absolute maximum insulin recommendation cap (e.g., 30 units) based on ADA safety standards.
- ⚡ **Panic Mode (Offline):** Provides instant (< 1s) GL estimations from a cached local database for emergency situations without internet connectivity.
- 📊 **Comprehensive Analytics:** Track your GL trends, carbohydrate intake, and meal timing through interactive charts.
- 🇻🇳 **Localized Vietnamese Database:** Curated nutrition data and density factors for 25 common Vietnamese dishes.

---

## 🏗 System Architecture

The application adopts a Polyglot Microservices architecture:

1. **Mobile App (Flutter):** Provides the cross-platform UI, state management via Provider, and the offline Panic Mode.
2. **API Gateway (Spring Boot):** Acts as the central orchestrator, handling routing, Redis caching, and Kafka event publishing for audit trails.
3. **Vision Service (FastAPI / Python):** Processes incoming images using ONNX-runtime (YOLOv8 & DAv2) to compute food volume via spatial integration ($V = \iint depth(x,y) \,dA$) and calculates GL using the nutrition DB.
4. **RAG Service (FastAPI / Python):** Performs hybrid search (ANN + BM25) over the `medical_knowledge` Milvus collection and interacts with Gemini 2.5 Flash to generate grounded clinical advice.

---

## 💻 Tech Stack

| Component | Technologies |
| --- | --- |
| **Frontend** | Dart, Flutter, Provider, fl_chart, GoRouter |
| **Gateway** | Java 17, Spring Boot, Spring WebClient, Redis, Kafka |
| **Computer Vision** | Python, FastAPI, ONNX Runtime, YOLOv8, Depth Anything V2 |
| **RAG & AI** | Python, FastAPI, Milvus, SentenceTransformers (`all-MiniLM-L6-v2`), Gemini API |
| **Infrastructure**| Docker, Docker Compose |

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Java 17+
- Python 3.10+
- Flutter 3.x
- Git

### Installation & Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/InSight.git
   cd InSight
   ```

2. **Start Infrastructure Services (Milvus, Redis, Kafka):**
   ```bash
   cd infra/docker
   docker compose up -d
   # Note: Wait ~45 seconds for Milvus to become completely healthy
   ```

3. **Start the Vision Service (Port 8000):**
   ```bash
   cd src/vision-service
   pip install -r requirements.txt
   python main.py
   ```

4. **Start the RAG Service (Port 8001):**
   ```bash
   cd src/rag-service
   pip install -r requirements.txt
   python main.py
   ```

5. **Start the API Gateway (Port 8080):**
   ```bash
   cd src/api-gateway
   ./gradlew bootRun
   ```

6. **Run the Flutter App:**
   ```bash
   cd mobile/insight_app
   flutter pub get
   flutter run -d chrome  # Or target an emulator/physical device
   ```

---

## 📂 Project Structure

```text
InSight/
├── data/                  # Vietnamese nutrition DB, density factors, and demo datasets
├── docs/                  # Architecture, Report, and Defense Preparation guides
├── infra/                 # Docker compose files for Milvus, Redis, Kafka
├── mobile/insight_app/    # Flutter application source code
├── src/
│   ├── api-gateway/       # Spring Boot orchestrator
│   ├── rag-service/       # FastAPI LLM & Vector DB integration
│   └── vision-service/    # FastAPI CV processing pipeline
└── README.md
```

---

## 🔬 Methodology & Safety

InSight employs rigorous medical safety constraints. The volume estimation relies on subtracting the 10th percentile of non-food pixel depths (table level) to isolate the food's relative height. We apply an empirical `solid_ratio` to correct for the water content in liquid dishes (e.g., Phở) to prevent dangerous overestimations of carbohydrates.

*For a detailed breakdown of our mathematical formulas and safety limits, please review the [Magic Numbers Defense Guide](./docs/magic_numbers_defense.md) and [Architecture Docs](./docs/architecture.md).*

---

## 📜 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments
- **USDA FoodData Central** for foundational nutritional data.
- **Vietnam National Institute of Nutrition** for localized food metrics.
- The **Depth Anything** and **Ultralytics YOLO** research teams.
- **Google Research** for the Nutrition5k dataset.
