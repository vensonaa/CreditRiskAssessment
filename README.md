# Credit Risk Assessment System

A comprehensive credit risk assessment system built with LangGraph, featuring a Reflection workflow pattern for automated report generation.

## Architecture

### Core Components
- **Generator Agent**: Understands user intent, creates execution plans, queries data, and generates initial credit risk assessment reports
- **Reflection Agent (Critic)**: Reviews generated reports with strict evaluation criteria and assigns quality scores
- **Refiner Agent**: Accepts critique and regenerates reports with corrections until quality threshold is met

### Technology Stack
- **Backend**: FastAPI with LangGraph for workflow orchestration
- **Frontend**: React with Vite for modern UI
- **AI Framework**: LangGraph for agent workflow management
- **Protocol**: MCP (Model Context Protocol) for skill integration
- **Database**: SQLite for data persistence

### Enhanced Data Tools
- **Loan Application Information Query Tool**: Retrieves loan application details, amounts, dates, purposes, and collateral information
- **Customer Information Query Tool**: Gets customer credit history, existing loans, financial metrics, and payment history
- **Compliance Requirements Retriever**: Checks KYC, AML, regulatory, and financial compliance requirements

## Features

### Generator Agent Capabilities
- Credit risk assessment report generation for submitted loan applications
- Tool inquiries and data retrieval
- User greeting and interaction
- Unsupported task detection
- Execution planning and data querying
- Loan application status validation

### Reflection Agent Evaluation Criteria
- **Accuracy**: Factual correctness and data precision
- **Completeness**: Coverage of all required assessment areas
- **Structure**: Logical organization and flow
- **Verbosity**: Appropriate level of detail
- **Relevance**: Pertinence to credit risk assessment
- **Tone**: Professional and appropriate communication style

### Quality Scoring
- Scores range from 0.0 to 1.0
- Automatic loop exit when score ≥ 0.8
- Actionable critique provided for scores < 0.8

### Refiner Agent Functions
- Accepts critique from Reflection agent
- Plans corrections based on feedback
- Retrieves missing data using tools
- Regenerates complete reports with improvements
- Continues loop until quality threshold is met

## Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
cd backend && python3 -m venv venv


source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Start the backend server
2. Start the frontend development server
3. Access the application at `http://localhost:5173`
4. Submit credit risk assessment requests
5. Monitor the Generator → Reflection → Refiner workflow
6. Review final generated reports

## Project Structure

```
CreditRiskAssessment/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── workflows/
│   │   ├── models/
│   │   ├── services/
│   │   └── api/
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Workflow Pattern

1. **Generator Agent**: Creates initial credit risk assessment report
2. **Reflection Agent**: Evaluates report quality and provides critique
3. **Refiner Agent**: Implements corrections and regenerates report
4. **Loop**: Continues until quality score ≥ 0.8
5. **Output**: Final high-quality credit risk assessment report

## MCP Integration

The system uses Model Context Protocol (MCP) for seamless skill integration through fast MCP servers, enabling:
- External data source connections
- Tool integration for data retrieval
- Scalable skill expansion
- Standardized communication protocols
