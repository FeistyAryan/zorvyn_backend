# 🚀 Zorvyn-Backend:

An asynchronous financial intelligence backend engineered for high-stakes B2B environments. This app is built with a focus on **traceability (Auditability)**, **Multi-vector Security**, and **Clean Architecture**, ensuring that the system remains scalable and maintainable as financial data complexity grows.

---

## 🛠️ Local Setup and Deployment

This app is fully containerized to ensure environment consistency and a "zero-config" startup experience for evaluators.

### **1. Prerequisites**
- **Docker** (Engine v20.10+)
- **Docker Compose** (v2.0+)

### **2. Quick Start**
```bash
# Initialize environment variables
cp .env.example .env

# Build and start all services (FastAPI, PostgreSQL, Redis)
docker compose up -d --build
```

### **3. Automatic Initialization**
*   **Alembic Migrations:** Automatically execute to synchronize the PostgreSQL schema on startup.
*   **Service Readiness:** The application utilizes Docker healthchecks to ensure the Database is fully initialized before the web server begins accepting traffic.
*   **Interactive Documentation:** Explore endpoints via **Swagger UI**: http://localhost:8000/docs

---

## 🧪 Manual Verification Guide (CURL)

Follow these steps to verify the system end-to-end. Ensure the containers are running (`docker compose up`).

### **1. Bootstrap the System (Admin Registration)**
The first user to register is automatically granted the **Admin** role.
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
-H "Content-Type: application/json" \
-d '{"email": "admin@zorvyn.com", "password": "AdminPassword123"}'
```

### **2. Login to receive Access Token**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
-H "Content-Type: application/json" \
-d '{"email": "admin@zorvyn.com", "password": "AdminPassword123"}'
```
*Note: Copy the `access_token` from the response.*

### **3. Create a Financial Record**
```bash
curl -X POST http://localhost:8000/api/v1/finance/create \
-H "Authorization: Bearer <YOUR_TOKEN>" \
-H "Content-Type: application/json" \
-d '{"amount": 50000, "type": "income", "category": "salary", "description": "Monthly Payout"}'
```

### **4. Get Dashboard Summary**
```bash
curl -X GET http://localhost:8000/api/v1/finance/summary \
-H "Authorization: Bearer <YOUR_TOKEN>"
```

### **5. Apply Advanced Filtering**
```bash
curl -X GET "http://localhost:8000/api/v1/finance/all?category=salary" \
-H "Authorization: Bearer <YOUR_TOKEN>"
```

---

## 🧪 Automated Testing Suite

The system includes a comprehensive suite of automated tests to ensure business logic integrity and RBAC enforcement.

### **Running the Tests**
To execute the full test suite within the containerized environment:
```bash
docker compose exec -e TESTING=True -e PYTHONPATH=. app pytest -v
```

### **Testing Strategy**
*   **Isolation:** Tests utilize an **In-Memory SQLite** database (configured in `tests/conftest.py`) to ensure each test runs in a clean, isolated environment without side-effects on the development database.
*   **Performance:** By setting `TESTING=True`, the `SlowAPI` rate limiter is bypassed, allowing the suite to run at maximum speed.
*   **Core Verifications:**
    *   **Auth Flow:** End-to-end registration, login, and secure token rotation.
    *   **RBAC Enforcement:** Validation of granular permissions for `Viewer`, `Analyst`, and `Admin` roles.
    *   **Financial Integrity:** Accurate calculation of dashboard summaries and transactional state management.
    *   **System Protection:** Hardcoded safeguards preventing the deactivation or downgrade of the primary System Administrator (ID 1).

---

## 📡 API Architecture & Integration Flow

This app’s API is designed to be **stateless**, **secure**, and **self-documenting**, focusing on a clean request-response lifecycle with built-in observability.

### **🔐 The Authentication Lifecycle (Hybrid Strategy)**
To maximize security, this app uses a **Double-Blind** approach for session management:
1.  **Login (`/auth/login`):** Exchanges credentials for a short-lived **Access Token** (returned in the JSON response) and a long-lived **Refresh Token** (set as a `HttpOnly`, `Secure` cookie).
2.  **Authorization:** Protected requests must include the Access Token in the `Authorization: Bearer <token>` header.
3.  **Refresh & Rotation:** When the access token expires, the client hits `/auth/refresh`. The system verifies the cookie, rotates the refresh token in the database (BCrypt-hashed), and issues a fresh pair to prevent **Token Replay** attacks.

### **📦 Core API Modules**
| Module | Endpoint Prefix | Key Capabilities |
| :--- | :--- | :--- |
| **Authentication** | `/api/v1/auth` | User registration, login, and secure token rotation. |
| **Finance Engine** | `/api/v1/finance` | Real-time dashboard summaries, advanced filtering, and CRUD operations. |
| **User Admin** | `/api/v1/users` | (Admin Only) User lifecycle management, role overrides, and status auditing. |

---

## 🏗️ Architectural Philosophy & Strategic Design

### **1. N-Tier Layered Architecture & SoC**
This app follows a strict N-Tier (Layered) design to ensure a clean **Separation of Concerns (SoC)**. This design is chosen to eliminate the "Ripple Effect"—preventing database schema changes from forcing a complete rewrite of the API layer.

*   **API Layer:** Concerned only with HTTP protocols, routing, and Pydantic-based contract validation. It is intentionally thin and **Interface Agnostic**.
    *   *Example:* If requirements shift from REST to **GraphQL**, only this transport layer is replaced; 100% of business logic remains intact.
*   **Service Layer (The Brain):** Orchestrates core business logic and side-effects. It ensures that complex operations, such as creating a financial record and logging an audit, are handled atomically.
*   **Repository Layer (Data Access):** Repositories are kept intentionally **"dumb."** They focus purely on SQL queries and CRUD operations.
    *   *Example:* If the project migrates from PostgreSQL to **another database**, only the Repository implementations change; the Service layer remains untouched.

### **2. One-Directional Dependency (Circular Import Prevention)**
To maintain a modular codebase, we enforce a **One-Directional Dependency Flow**: 
`API -> Service -> Repository -> Model`.
*   **Logic Isolation:** Repositories have zero knowledge of API routers, preventing business logic from leaking into the data access layer and inherently neutralizing circular import risks.

### **3. Request-Scoped State Isolation (Constructor Injection)**
We avoid the Singleton pattern for services to prevent **State Leakage** in high-concurrency asynchronous environments.
*   **Mechanism:** Every service is instantiated per request with its own dedicated `AsyncSession`.
*   **Benefit:** This guarantees strict **Request Isolation**, ensuring that database transactions are thread-safe and the system remains highly testable.

---

## 📈 Future Scaling & Data Strategy

### **1. Analytical Scaling: Transitioning to Materialized Views**
As financial datasets grow significantly, real-time aggregations on transactional tables can impact performance. The app’s architecture is designed to seamlessly transition to an **OLAP-ready strategy**:
*   **Abstraction Layer:** Because data access is isolated in Repositories, we can swap real-time calculations for **PostgreSQL Materialized Views** without modifying service-layer logic.
*   **Efficiency:** This ensures sub-millisecond response times for dashboard summaries even as transaction volumes scale to millions of rows.

### **2. Fault-Tolerant Auditing (Traceability & Failure Isolation)**
In financial systems, **Traceability is non-negotiable**. Every mutation must be recorded for compliance, reconciliation, and security auditing.
*   **Decision:** Auditing is performed via asynchronous **Background Tasks**.
*   **Rationale:** While traceability is critical, user-facing latency must not suffer. By decoupling the audit trail, we ensure a seamless experience without sacrificing financial integrity.
*   **Isolation:** The audit worker spawns a fresh `AsyncSession` via an independent factory. This ensures that even if the main transaction rolls back or the session closes, the audit attempt maintains its own dedicated lifecycle, providing **True Failure Isolation**.

---

## 🛡️ Multi-Vector Security Model

### **🔐 Hybrid Token Strategy (Double-Blind Auth)**
*   **Access Tokens:** Short-lived JWTs sent via the `Authorization: Bearer` header (CSRF resistant).
*   **Refresh Tokens:** Stored in **HttpOnly, Secure Cookies** (XSS resistant).
*   **Zero-Trust Storage:** All refresh tokens are **one-way hashed (BCrypt)** in the database. Even a full DB leak cannot compromise active user sessions.
*   **Strict Rotation:** Every refresh cycle invalidates the used token and issues a fresh pair, effectively mitigating **Token Replay Attacks**.

---

## 👥 User Roles & Access Control (RBAC)

| Feature | Viewer | Analyst | Admin |
| :--- | :---: | :---: | :---: |
| View Records & Summaries | ✅ | ✅ | ✅ |
| Create & Update Records | ❌ | ✅ | ✅ |
| Soft-Delete Records | ❌ | ❌ | ✅ |
| User & Role Management | ❌ | ❌ | ✅ |

### **Business Logic & Assumptions**
*   **First-User Bootstrap:** To facilitate initial setup, the very first user to register is automatically granted the **Admin** role. All subsequent registrations default to the **Viewer** role.
*   **Admin Protection:** The primary system administrator (User ID 1) is protected via service-layer logic, preventing unauthorized role downgrades or account deactivation.
*   **Viewer:** Stakeholders who monitor trends without data modification rights.
*   **Analyst (The B2B Operator):** In professional dashboards, analysts manage client data entry and corrections, justifying their `Create` and `Update` permissions.
*   **Admin:** Reserved for high-stakes operational control and administrative overrides.

---

## 🔍 Observability & Reliability

### **1. Unified Error Handling & Predictability**
The system uses a **Custom Exception Hierarchy**. Every application-specific error (Auth, Permission, Not Found) is intercepted by a global handler that returns a consistent JSON structure, ensuring the API remains predictable for frontend consumers.

### **2. Distributed Tracing & Correlation IDs**
Every request is assigned a unique UUID via custom ASGI middleware. This ID is:
*   Injected into every structured **JSON log** message for effortless debugging across the service layer.
*   Returned in the **`X-Correlation-ID`** header, enabling frontend developers to provide a unique reference code for troubleshooting.

---

## 📂 Project Structure Snapshot
```text
app/
├── api/v1/             # Transport Layer: Routing & RBAC enforcement
├── core/               # Backbone: Configuration, Security, & Middlewares
├── models/             # Data Definition: Single source of truth (SQLModel)
├── repositories/       # Data Access: Isolated SQL queries & CRUD
├── schemas/            # Contracts: Pydantic models for I/O validation
└── services/           # Logic Layer: Business workflows & orchestrations
```
