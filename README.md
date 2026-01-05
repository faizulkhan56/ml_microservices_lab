# ML Microservices Lab (2 Services) — Theory + Hands-on

This repository contains a complete, runnable **two-microservice** lab for a simple machine-learning-style system:

- **Service A (Input Logger / Gateway)**: Receives client requests, logs inputs, and optionally forwards the request to the ML service.
- **Service B (ML Predictor)**: A dedicated service that returns a mock "prediction" (random class + confidence) for demo purposes.

The project is designed to teach both:
1) **Microservices theory (why/how)**, and  
2) The **practical workflow** of running two independent services that communicate over HTTP.

---

## Repo structure

```text
ml_microservices_lab/
├── service_a/
│   ├── main.py
│   └── requirements.txt
├── service_b/
│   ├── main.py
│   └── requirements.txt
├── .gitignore
└── README.md
```

> **Recommended local practice:** create a **separate Python virtual environment (venv) per service**.
That mirrors real microservices deployments (one container/image per service).

---

# Part 1 — Microservices Concepts (Complete Theory)

## 1) Monolithic vs Microservices

### Monolithic architecture
A monolith is a single deployable unit where UI, business logic, and data access are tightly coupled.

**Pros:**
- Simple at the beginning
- Easy local debugging
- Single deployment pipeline

**Cons (especially for ML systems):**
- Hard to scale specific parts (inference vs training)
- Technology lock-in (one stack for everything)
- Risky deployments (small change redeploys everything)
- Slower teams (coordination & merge conflicts)
- ML workflows are diverse (data ingestion, preprocessing, training, inference all need different resources)

### Microservices architecture
Microservices split the system into **small independent services** that communicate via APIs.

**Key principles:**
- **Single responsibility**: one service does one job well
- **Autonomy**: services build/deploy/scale independently
- **Resilience**: failure stays contained
- **Polyglot**: each service can choose the best tech stack
- **Decentralized data**: each service may own its own storage if needed

**Why microservices fit ML:**
- Inference scales with traffic; training scales with data/model complexity
- Different services can use different frameworks (FastAPI, TensorFlow, PyTorch, Spark, etc.)
- You can deploy new model versions with lower blast radius
- Observability can be ML-aware (latency + drift + model performance)

---

## 2) Core services in an ML microservices platform

Common ML microservices you’ll see in real systems:

- **Data Ingestion**: pulls data from sources (APIs, DBs, streams)
- **Preprocessing**: cleans / normalizes / transforms raw data
- **Feature Store**: centralized feature definitions + online/offline access
- **Training Service**: runs training jobs, hyperparameter tuning, evaluation
- **Model Registry**: versioned model artifacts + metadata + approvals
- **Inference / Model API**: exposes prediction endpoints with SLA requirements
- **Monitoring**: technical + ML signals (latency, errors, drift, model decay)
- **Orchestration**: workflow engines (Airflow, Argo Workflows, etc.)
- **CI/CD**: pipelines for code + model promotion

This lab focuses on a **minimal** slice:
- Service A = gateway/logging/orchestration
- Service B = inference service (mock model)

---

## 3) Communication patterns between services

### REST (HTTP + JSON)
- Human-friendly, widely supported, easy testing with curl
- Great for request/response interactions
- Downsides: overhead of HTTP/JSON, less ideal for high-frequency low-latency calls

### gRPC (protobuf)
- Fast binary format, strong contracts, streaming support
- Great for internal service-to-service communication at scale
- Downsides: extra tooling + learning curve

### Message queues (Kafka, RabbitMQ, Pulsar)
- Asynchronous, decoupled communication
- Great for pipelines, buffering spikes, and event-driven architectures
- Patterns: pub-sub, point-to-point, request-reply, DLQ

This lab uses **REST** (simplest to learn and test).

---

## 4) Stateless vs Stateful services

### Stateless service
Does NOT store client session state between requests.
- Easy horizontal scaling
- Easy recovery (just restart instances)

**Examples:**
- Inference service that predicts based only on input payload
- Validation or transformation services

### Stateful service
Keeps state across requests (in memory or tied to persistent storage).
- Harder to scale
- Needs replication/sharding/consistency planning

**Examples:**
- Feature store, model registry, online learning, session-based recommenders

This lab's services are **stateless** (aside from logs / in-memory model object).

---

## 5) Docker and microservices (conceptual)

In production, microservices are commonly shipped as containers:
- each service → its own image
- dependencies isolated
- portable across dev/stage/prod
- health checks + resource limits

In this lab we use **venv** to keep dependencies isolated locally.
(Think: `venv` ≈ local substitute for a Docker image.)

---

# Part 2 — The Actual Lab Implementation (2 Services)

## High-level flow

1. Client sends request to **Service A**:
   - `POST http://localhost:8000/process`
   - body: `{ "data": "...", "forward_to_model": true/false }`

2. Service A logs the input and:
   - If `forward_to_model=false`: returns logging status only
   - If `forward_to_model=true`: calls Service B `POST http://localhost:8001/predict`

3. Service B returns a mock prediction (random class + confidence)

4. Service A returns a combined response.

---

# Part 3 — Setup & Run (Ubuntu/Debian safe way)

> If you are on Ubuntu/Debian with Python 3.12+, you may see:
> `error: externally-managed-environment` (PEP 668).
> The fix is to use a **virtual environment** (venv). Do **not** install packages system-wide.

## 0) Prerequisites

```bash
sudo apt update
sudo apt install -y python3-full python3-venv
```

---

## 1) Run Service B (Terminal 1)

```bash
cd service_b

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

Service B will run on: `http://localhost:8001`

Health check:
```bash
curl http://localhost:8001/health
```

---

## 2) Run Service A (Terminal 2)

```bash
cd service_a

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

Service A will run on: `http://localhost:8000`

Health check:
```bash
curl http://localhost:8000/health
```

---

# Part 4 — Test the lab (curl)

## 1) Service A without forwarding (only logging)

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"data":"sample input","forward_to_model":false}' \
  http://localhost:8000/process
```

Expected response (example):
```json
{"status":"Input logged successfully"}
```

## 2) Service A with forwarding (A → B)

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"data":"cat image data","forward_to_model":true}' \
  http://localhost:8000/process
```

Expected response (example):
```json
{
  "status": "Input logged successfully",
  "model_prediction": {
    "prediction": {
      "class": "dog",
      "confidence": 0.92,
      "input_length": 13
    },
    "message": "Predicted class: dog with 92.0% confidence"
  }
}
```

## 3) Call Service B directly

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"input":"test input"}' \
  http://localhost:8001/predict
```

---

# Part 5 — Troubleshooting (Do not skip)

## A) `error: externally-managed-environment` (PEP 668)

**Cause:** OS-managed Python blocks system-wide pip installs.  
**Fix (recommended):** Use venv:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Avoid:** `pip install --break-system-packages` (risk of breaking your OS Python).

---

## B) Port already in use (8000 or 8001)

Symptoms:
- `Address already in use`
- Service won't start

Find the process:
```bash
sudo lsof -i :8000
sudo lsof -i :8001
```

Kill it (example PID):
```bash
sudo kill -9 <PID>
```

---

## C) Service A returns 503 "Service B is unavailable"

Cause:
- Service B isn't running
- Wrong port
- Network restriction

Fix checklist:
1. Start Service B first
2. Verify:
   ```bash
   curl http://localhost:8001/health
   ```
3. Confirm Service A has:
   - `SERVICE_B_URL = "http://localhost:8001/predict"`

---

## D) Wrong python/pip being used

If you suspect you're not inside venv:
```bash
which python
which pip
python --version
```

Inside venv, `which python` should point to:
`.../service_x/venv/bin/python`

---

## E) `ModuleNotFoundError` for installed packages

Usually means:
- venv not activated
- installed packages into another environment

Fix:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## F) Uvicorn reload issues (inside some containers/VM setups)

`reload=True` is great for local dev, but can be noisy in certain environments.

You can disable reload by editing main.py:
- Service A: `reload=False`
- Service B: `reload=False`

Or run directly with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
uvicorn main:app --host 0.0.0.0 --port 8001
```

---

# Part 6 — What to improve next (real production direction)

This lab intentionally uses simple choices. In real systems, you’d typically add:

- **Service discovery**: DNS/Consul/etcd instead of hard-coded URLs
- **Resilience patterns**: retries, timeouts, circuit breakers, fallbacks
- **Async messaging**: Kafka/RabbitMQ/Pulsar to decouple pipelines
- **Observability**: OpenTelemetry traces, metrics, structured logs
- **Containerization**: Dockerfile + compose/Kubernetes manifests
- **Security**: authn/authz, mTLS, rate limiting

---

## License
MIT (use freely for learning and demos)
