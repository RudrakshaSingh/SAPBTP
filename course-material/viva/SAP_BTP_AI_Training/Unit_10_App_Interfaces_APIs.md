# 🌐 Unit 10 — App Interfaces & APIs

> **Module**: Module 4 — Generative AI  
> **Duration**: Day 18–19 (16 hours)  
> **Dates**: 22-Jul-2026, 23-Jul-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — API Fundamentals

### Q1. What is an API? Why are APIs critical in GenAI applications?

**A:** An **API (Application Programming Interface)** is a contract that allows software systems to communicate with each other. It defines what requests are valid, what data can be sent, and what responses to expect.

**Why APIs are critical in GenAI:**

| Reason | Explanation |
|--------|-------------|
| **LLM access** | ChatGPT, Gemini, Claude are all accessed via APIs |
| **Microservices** | GenAI components (retrieval, generation, embedding) communicate via APIs |
| **Integration** | Connect AI capabilities to existing business systems |
| **Abstraction** | Use AI models without knowing their internal implementation |
| **Scalability** | APIs enable distributed, cloud-native architectures |

**Real flow:** Your RAG app → `POST /ask` → Your FastAPI → Embedding API → Vector Search → Gemini API → Response.

---

### Q2. What is REST? What are REST principles?

**A:** **REST (Representational State Transfer)** is an architectural style for designing APIs. RESTful APIs use HTTP and follow 6 constraints:

| Principle | Meaning |
|-----------|---------|
| **Client-Server** | Client and server are separate; client doesn't know server implementation |
| **Stateless** | Each request contains all info needed; server keeps no client session |
| **Cacheable** | Responses can be cached by client/intermediary |
| **Uniform Interface** | Consistent URLs, HTTP methods, response formats |
| **Layered System** | Client can't tell if it's talking to the actual server or a proxy/load balancer |
| **Code on Demand** (optional) | Server can send executable code to client |

**Most important in practice:** Stateless + Uniform Interface.

---

### Q3. Explain HTTP methods. Which does your project use?

**A:**

| Method | Purpose | Idempotent? | Body? | Our Project |
|--------|---------|------------|-------|-------------|
| `GET` | Read/retrieve data | ✅ Yes | No | `/`, `/health` |
| `POST` | Create/send data | ❌ No | Yes (JSON) | `/ingest`, `/ask` |
| `PUT` | Replace entire resource | ✅ Yes | Yes | Not used |
| `PATCH` | Partially update resource | ❌ No | Yes | Not used |
| `DELETE` | Remove resource | ✅ Yes | No | Not used |
| `HEAD` | Like GET but no body (check existence) | ✅ Yes | No | Not used |
| `OPTIONS` | List allowed methods (CORS preflight) | ✅ Yes | No | Auto (FastAPI) |

**Why `/ask` uses POST:** We're sending a question in the request body. GET requests shouldn't have a body and would expose the question in the URL (bad for privacy/logging).

---

### Q4. What are HTTP status codes? List the important ones.

**A:**

| Range | Category | Common Codes |
|-------|----------|-------------|
| **2xx** | Success | 200 OK, 201 Created, 204 No Content |
| **3xx** | Redirection | 301 Moved Permanently, 302 Found, 304 Not Modified |
| **4xx** | Client Error | 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity, 429 Too Many Requests |
| **5xx** | Server Error | 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout |

**Most relevant for our project:**
- `200 OK` — Successful GET/POST response.
- `201 Created` — Resource created (we return 200 for simplicity).
- `422 Unprocessable Entity` — FastAPI returns this when Pydantic validation fails.
- `500 Internal Server Error` — Unhandled exception (e.g., Gemini API fails).

---

### Q5. What are HTTP headers? Name the important ones.

**A:** **Headers** carry metadata about the request or response.

| Header | Type | Purpose | Example |
|--------|------|---------|---------|
| `Content-Type` | Request/Response | Format of the body | `application/json` |
| `Accept` | Request | Expected response format | `application/json` |
| `Authorization` | Request | Authentication credentials | `Bearer eyJhbGci...` |
| `X-API-Key` | Request | API key authentication | `X-API-Key: abc123` |
| `Cache-Control` | Response | Caching instructions | `no-cache`, `max-age=3600` |
| `CORS` headers | Response | Cross-origin access control | `Access-Control-Allow-Origin: *` |
| `X-Request-ID` | Both | Track requests across systems | `X-Request-ID: uuid` |

---

## 🔹 Section 2 — FastAPI Deep Dive

### Q6. What makes FastAPI special? Compare it to Flask and Django.

**A:**

| Feature | Flask | Django | FastAPI |
|---------|-------|--------|---------|
| **Speed** | Moderate | Moderate | Very fast (Starlette, async) |
| **Type hints** | No | No | ✅ First-class |
| **Auto documentation** | No | No | ✅ Swagger + ReDoc |
| **Validation** | Manual | Form-based | ✅ Pydantic automatic |
| **Async support** | Limited | Limited | ✅ Native async/await |
| **Learning curve** | Low | High | Low-Medium |
| **Batteries** | Minimal | Full (ORM, auth, admin) | Minimal (focused) |
| **Best for** | Microservices | Full web apps | APIs, microservices, GenAI backends |

**Why FastAPI for GenAI:**
- LLM calls are I/O-bound → perfect for `async def`.
- Pydantic schemas double as input validation AND documentation.
- Auto-generated Swagger UI (`/docs`) means no manual API docs.
- Type hints help IDEs catch errors before runtime.

---

### Q7. Explain FastAPI's request lifecycle.

**A:**

```
1. HTTP Request arrives
        ↓
2. Routing — Match URL + method to endpoint function
        ↓
3. Dependency Injection — Resolve any dependencies
        ↓
4. Request validation — Pydantic validates request body, path params, query params
        ↓
5. Endpoint function executes — Your business logic
        ↓
6. Response validation — Validate return value against response_model
        ↓
7. Serialization — Convert Pydantic model to JSON
        ↓
8. HTTP Response sent
```

---

### Q8. What are path parameters, query parameters, and request body?

**A:**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# PATH PARAMETER: In the URL path, required
@app.get("/users/{user_id}")
def get_user(user_id: int):  # Extracted from URL
    return {"user_id": user_id}
# GET /users/42 → user_id = 42

# QUERY PARAMETER: After ? in URL, optional by default
@app.get("/users/")
def list_users(skip: int = 0, limit: int = 10, active: bool = True):
    ...
# GET /users/?skip=20&limit=5&active=false

# REQUEST BODY: JSON payload, for POST/PUT
class UserCreate(BaseModel):
    name: str
    email: str
    salary: float

@app.post("/users/")
def create_user(user: UserCreate):  # Body automatically parsed
    return {"created": user.name}
# POST /users/ with body: {"name": "Rudra", "email": "...", "salary": 85000}
```

---

### Q9. What is dependency injection in FastAPI?

**A:** **Dependency injection** is a pattern where FastAPI automatically provides dependencies to your endpoint functions.

```python
from fastapi import Depends, HTTPException, Header

# Define a dependency
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "secret123":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Use the dependency
@app.get("/protected/")
def protected_route(api_key: str = Depends(verify_api_key)):
    return {"message": "You are authorized!"}

# Database connection dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
def get_users(db = Depends(get_db)):
    return db.query(User).all()
```

---

### Q10. How do you handle errors in FastAPI?

**A:**

```python
from fastapi import HTTPException

@app.post("/ask")
def ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        result = llm.invoke(prompt)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI service unavailable: {str(e)}"
        )

    return AskResponse(answer=result.answer, source_used=sources)

# Custom exception handler
from fastapi.responses import JSONResponse
from fastapi import Request

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
```

---

## 🔹 Section 3 — API Design

### Q11. What are REST API best practices?

**A:**

| Practice | Good | Bad |
|----------|------|-----|
| **Use nouns, not verbs** | `/users/`, `/documents/` | `/getUsers`, `/deleteDoc` |
| **Use plural nouns** | `/users/42` | `/user/42` |
| **HTTP methods carry meaning** | `DELETE /users/42` | `POST /deleteUser` |
| **Versioning** | `/api/v1/users/` | `/users/` (breaking changes) |
| **Consistent response structure** | Always `{data, error, meta}` | Different structure per endpoint |
| **Meaningful status codes** | 404 for not found | Always return 200 |
| **Pagination** | `?page=2&per_page=20` | Return all records |
| **Filter via query params** | `/users?role=admin` | Different URL per filter |
| **Document your API** | OpenAPI/Swagger | No documentation |

---

### Q12. What is CORS? Why does it matter for web applications?

**A:** **CORS (Cross-Origin Resource Sharing)** is a browser security mechanism that blocks web pages from making requests to a different domain/origin than the one that served the page.

**The problem:**
```
Your frontend at http://localhost:3000
   → tries to call http://localhost:8000/api/ask
   Browser blocks this! (different port = different origin)
```

**FastAPI CORS fix:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**For development:** `allow_origins=["*"]` allows all origins (never use in production).

---

### Q13. What is API authentication? What are the common methods?

**A:**

| Method | How It Works | Security | Use Case |
|--------|-------------|----------|----------|
| **API Key** | Client sends key in header | Low-Medium | Internal/trusted clients |
| **Basic Auth** | Base64 encoded username:password | Low | Legacy systems |
| **Bearer Token (JWT)** | Signed token with user info and expiry | High | Web apps, SPAs |
| **OAuth 2.0** | Authorization framework for delegated access | High | "Login with Google", third-party access |
| **mTLS** | Both client and server present certificates | Very High | Service-to-service in enterprise |

**JWT (JSON Web Token):**
```
header.payload.signature
eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ1c2VyMSIsImV4cCI6MTcyMzAwMH0.aB3cD4...
```

- **Header:** Algorithm used (`RS256`)
- **Payload:** Claims (user ID, expiry, roles)
- **Signature:** Cryptographic proof of integrity

---

### Q14. What is API rate limiting?

**A:** **Rate limiting** restricts how many requests a client can make in a given time period to prevent abuse and manage costs.

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/ask")
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
async def ask(request: Request, req: AskRequest):
    ...
```

**Common rate limiting strategies:**
- **Fixed window:** N requests per time period (resets at period boundary).
- **Sliding window:** N requests in the last N seconds (smoother).
- **Token bucket:** Tokens are added at a fixed rate; each request consumes a token.

**HTTP 429 Too Many Requests** is returned when limit is exceeded.

---

## 🔹 Section 4 — API Documentation & Testing

### Q15. What is OpenAPI/Swagger?

**A:** **OpenAPI** (formerly Swagger) is a standard specification for documenting REST APIs. FastAPI auto-generates OpenAPI documentation.

**FastAPI provides two UIs:**
- **`/docs`** — Swagger UI (interactive, can test endpoints).
- **`/redoc`** — ReDoc (cleaner read-only documentation).

```python
app = FastAPI(
    title="Document Q&A API",
    description="RAG-based document question answering system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask a question about documents",
    description="Uses RAG to retrieve relevant context and generate a grounded answer.",
    responses={
        200: {"description": "Successful answer"},
        422: {"description": "Validation error"},
        503: {"description": "AI service unavailable"}
    }
)
def ask(req: AskRequest):
    ...
```

---

### Q16. How do you test APIs? What tools can you use?

**A:**

| Tool | Type | How to Use |
|------|------|-----------|
| **Swagger UI** (`/docs`) | Browser | Interactive testing in browser |
| **curl** | CLI | `curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question":"How many leaves?"}'` |
| **Postman** | GUI | Full-featured API testing client |
| **httpie** | CLI | `http POST localhost:8000/ask question="How many leaves?"` |
| **pytest + httpx** | Unit/integration | Automated API testing |

**FastAPI testing with pytest:**
```python
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ask():
    response = client.post("/ask", json={"question": "How many leaves?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "source_used" in data
```

---

## 🔹 Section 5 — UI for GenAI Applications

### Q17. What are the options for building GenAI user interfaces?

**A:**

| Option | Tech Stack | Best For |
|--------|-----------|----------|
| **Swagger UI** (auto) | FastAPI | Developer testing |
| **Streamlit** | Python | Data scientists, rapid prototyping |
| **Gradio** | Python | ML demos, Hugging Face Spaces |
| **React/Vue** | JavaScript | Production web apps |
| **Next.js** | React + Node.js | Full-stack web apps |
| **SAP Build** | Low-code | SAP ecosystem UIs |
| **SAP Fiori** | JavaScript/UI5 | SAP enterprise applications |

---

### Q18. What is streaming in GenAI UIs?

**A:** **Streaming** sends LLM output token by token as it's generated, rather than waiting for the complete response. This makes the UI feel much faster and more responsive.

```python
# FastAPI streaming endpoint
from fastapi.responses import StreamingResponse

@app.post("/ask/stream")
async def ask_stream(req: AskRequest):
    async def generate():
        async for chunk in llm.astream(prompt):
            yield f"data: {chunk.content}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"  # SSE (Server-Sent Events)
    )

# Client (JavaScript):
const response = await fetch('/ask/stream', {method: 'POST', body: ...});
const reader = response.body.getReader();
while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    document.getElementById('answer').textContent += new TextDecoder().decode(value);
}
```

**SSE vs WebSocket:**
- **SSE (Server-Sent Events):** One-way server→client streaming. Simpler, works over HTTP. Perfect for LLM token streaming.
- **WebSocket:** Full-duplex (both directions). More complex. Better for real-time chat, collaborative apps.

---

### Q19. What is SAP BTP Application Development? What tools are available?

**A:**

| Tool | What It Is | Best For |
|------|-----------|----------|
| **SAP Build Apps** | Low-code/no-code app builder | Business apps without coding |
| **SAP Build Process Automation** | Workflow + RPA automation | Business process automation |
| **CAP (Cloud Application Programming)** | Node.js/Java framework | Custom SAP extensions |
| **SAP Fiori** | Design system + framework | SAP-style enterprise UIs |
| **SAP BTP Workzone** | Portal + collaboration | Employee experience portals |
| **Cloud Foundry** | PaaS runtime | Deploy Node.js, Python, Java apps |
| **Kyma** | Kubernetes runtime | Containerized microservices |

---

## 🔹 Section 6 — Webhooks & Async Patterns

### Q20. What is a webhook?

**A:** A **webhook** is a way for one application to notify another when an event happens — an "HTTP callback."

```
Traditional (polling):     Your app → "Any news?" → Server: "No" (repeat every 5s)
Webhook (event-driven):    Server → "Here's new data!" → Your app (only when something happens)
```

**Example:** GitHub sends a POST request to your webhook URL whenever code is pushed to a repository. This triggers your CI/CD pipeline.

```python
@app.post("/webhook/document-uploaded")
def handle_document_upload(event: dict):
    # Called by document storage service when a new document is uploaded
    doc_url = event["url"]
    ingest_document(source=doc_url, text=fetch_text(doc_url))
    return {"status": "ingested"}
```

---

### Q21. What is async/await in Python? How does it apply to GenAI APIs?

**A:**

```python
import asyncio

# Synchronous (blocking): One request blocks the server
def ask_sync(req: AskRequest):
    result = llm.invoke(prompt)  # Server blocked for 3 seconds!
    return AskResponse(answer=result.answer)

# Asynchronous (non-blocking): Server can handle other requests while waiting
async def ask_async(req: AskRequest):
    result = await llm.ainvoke(prompt)  # Yields control; handles other requests
    return AskResponse(answer=result.answer)
```

**Why async matters for GenAI:**
- LLM API calls take 1-10 seconds.
- With sync endpoints, 10 concurrent users → server blocked for 10-100s for each.
- With async, server handles hundreds of concurrent requests efficiently.

**FastAPI supports both** `def` (runs in thread pool) and `async def` (native async) endpoints.

---

## 🔹 Section 7 — Quick Fire Questions

### Q22. What is the difference between REST and GraphQL?

**A:**

| Aspect | REST | GraphQL |
|--------|------|---------|
| **Data fetching** | Fixed endpoints return fixed structure | Client specifies exact fields needed |
| **Over-fetching** | Common (get all fields, use few) | Never (get only what you ask for) |
| **Under-fetching** | Common (need multiple calls) | Never (one query for all data) |
| **Versioning** | `/v1`, `/v2` endpoints | Schema evolves without versioning |
| **Complexity** | Simpler | More complex setup |

---

### Q23. What is an API gateway?

**A:** An **API gateway** is a single entry point for all API requests. It handles:
- **Authentication** — Verify API keys, JWT tokens.
- **Rate limiting** — Throttle excessive requests.
- **Load balancing** — Distribute traffic across backend servers.
- **SSL termination** — Handle HTTPS at the gateway.
- **Logging/monitoring** — Centralized request tracking.
- **Routing** — Forward requests to the right microservice.

**Examples:** AWS API Gateway, Kong, Nginx, SAP API Management.

---

### Q24. What is idempotency in APIs?

**A:** A request is **idempotent** if making it multiple times has the same effect as making it once.

| Method | Idempotent? | Why |
|--------|------------|-----|
| GET | ✅ Yes | Just reading, no side effects |
| DELETE | ✅ Yes | Deleting already-deleted item → same result |
| PUT | ✅ Yes | Replacing with same data → same result |
| POST | ❌ No | Each call creates a new resource |
| PATCH | ❌ Usually No | `"increment by 1"` is not idempotent |

**Important for retries:** If a network error occurs, retrying an idempotent request is safe. Retrying a POST could create duplicates.

---

### Q25. What is the difference between JSON and XML?

**A:**

| Aspect | JSON | XML |
|--------|------|-----|
| **Syntax** | `{"key": "value"}` | `<key>value</key>` |
| **Verbosity** | Less verbose | Very verbose |
| **Readability** | High | Lower |
| **Data types** | String, number, boolean, null, object, array | All text (need schema for types) |
| **Parsing** | Fast | Slower |
| **Web APIs** | Dominant standard | Legacy enterprise, SOAP |

---

> **💡 Viva Tip:** In the API context, always relate back to your FastAPI project. If asked "what is a REST endpoint?" — walk through your `/ask` endpoint specifically. Concrete examples from your own code score much higher than textbook definitions.

---

*End of Unit 10 — App Interfaces & APIs 🌐*
