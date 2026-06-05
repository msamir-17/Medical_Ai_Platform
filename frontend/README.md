# MediAI: Clinical Document Intelligence & Risk Analysis Platform

Transform medical reports into structured insights using OCR, NLP, Machine Learning, and Retrieval-Augmented Generation (RAG).

## Overview

MediAI helps users understand and organize medical records that are stored as PDFs or scanned reports. The platform extracts clinical information, predicts disease risk, explains model decisions using SHAP, and allows users to ask questions about their reports through an AI-powered chat interface.

---

## Inspired by Industry Challenge

This project was inspired by a healthcare problem highlighted in Razorpay's Fix My Itch initiative:

> Patients often receive different diagnoses, treatment plans, or prescriptions from multiple doctors and struggle to understand whether these differences are expected or require further investigation.

MediAI addresses part of this challenge by converting medical reports into structured data and providing a unified view of a patient's health history.

---

## How It Works

```text
Medical Report
      │
      ▼
   EasyOCR
      │
      ▼
 BioBERT NLP
      │
      ▼
Structured Data
      │
 ┌────┴────┐
 ▼         ▼
Risk ML   FAISS
Models    Vector DB
 ▼         ▼
SHAP      RAG Chat
```

---

## Key Features

* Upload PDF and image-based medical reports
* Extract diseases, medications, and lab values
* Predict diabetes and cardiac risk
* Explain predictions with SHAP
* AI chatbot for report-specific Q&A
* Secure user-level data isolation

---

## Engineering Challenges Solved

### Preventing RAG Hallucinations

Created report-specific vector indexes so the chatbot only retrieves information from the selected report.

### OCR Quality Issues

Switched to a vision-based OCR pipeline to improve extraction accuracy on scanned clinical reports.

### Medical Term Normalization

Used RapidFuzz to correct OCR spelling mistakes in medical terminology before NLP processing.

---

## AI & ML Stack

* EasyOCR for document text extraction
* BioBERT for medical entity recognition
* XGBoost for disease risk prediction
* SHAP for model explainability
* Llama 3.1 8B for RAG-based conversations
* FAISS for vector search

---

## Performance

| Metric               | Result      |
| -------------------- | ----------- |
| OCR Accuracy         | ~99%        |
| Cardiac Risk ROC-AUC | 95.1%       |
| Cardiac Risk Recall  | 96%         |
| Diabetes Accuracy    | 81.5%       |
| Processing Time      | < 2 seconds |

---

## Tech Stack

**Frontend**

* Next.js 14
* TypeScript
* Tailwind CSS
* Zustand

**Backend**

* FastAPI
* SQLAlchemy
* Pydantic

**Database**

* PostgreSQL (Supabase)
* FAISS

**Infrastructure**

* Docker
* Docker Compose
* Resend

---

## Security

* JWT Authentication
* User-level data isolation
* Secure environment variables
* Protected API endpoints

---

## Trade-offs

* Chose XGBoost over deep learning because healthcare datasets were relatively small.
* Used FAISS for simplicity and low infrastructure cost during development.
* Prioritized explainability through SHAP rather than using black-box models.

---

## Future Improvements

* Longitudinal health tracking
* Async OCR processing with Celery
* Distributed vector database support
* Doctor collaboration and secure report sharing

---

## Screenshots

### Dashboard

![Dashboard](images/dashboard.png)

### SHAP Explanation

![SHAP](images/shap.png)

### AI Chat

![Chat](images/chat.png)

---

## Local Setup

```bash
git clone <repo-url>
cd mediai

docker-compose up --build
```

Required environment variables:

```env
DATABASE_URL=
GROQ_API_KEY=
JWT_SECRET=
RESEND_API_KEY=
```

---

## Tech Focus

This project explores how OCR, biomedical NLP, machine learning, explainability, and RAG can be combined to build practical healthcare applications.
