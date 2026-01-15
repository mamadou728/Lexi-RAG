# 🏛️ Lexi-RAG: A Privacy-First Legal Retrieval System
**_AI-powered legal retrieval system built for privacy, precision, and trust._**
**_Personal Project — In Progress_**

---

## 🧠 What Is Lexi-RAG?

Lexi-RAG is a **personal AI engineering project** exploring how **Retrieval-Augmented Generation (RAG)** can power a **law-firm knowledge system** designed around privacy, access control, and real-world security constraints.

Rather than building a generic RAG chatbot, this project focuses on **how retrieval systems operate in high-risk environments**, where every query and document must respect **confidentiality, encryption, and legal privilege**.

> _Goal: Learn how to design intelligent retrieval systems that remain safe, private, and compliant in data-sensitive industries._

---

## ⚖️ Why a Law-Firm Use Case?

Law firms generate massive volumes of **unstructured information** — contracts, filings, memos, emails, evidence, and invoices — all protected by confidentiality agreements.
Because this data rarely follows a fixed schema, **MongoDB** is used to store it flexibly while still supporting structured queries.

Lexi-RAG envisions a secure AI assistant that helps each role differently:
- **Lawyers and partners:** Search legal clauses, filings, and case summaries
- **Paralegals and clerks:** Organize evidence and deadlines
- **Intake admins:** Manage client onboarding and schedules
- **Clients:** View their own case status and shared materials only

Everything operates under strict privacy layers to preserve legal privilege.

---

## 🧰 Tech Stack

**Backend**
- Python (FastAPI)

**Frontend**
- Next.js

**Databases**
- MongoDB — unstructured legal documents & metadata
- Qdrant — vector embeddings and semantic search

**AI / RAG**
- LLM: TBD (low-cost text model, subject to change)
- Embeddings: TBD (to be selected after benchmarking)

**Infrastructure**
- Docker

---

## 💡 Project Purpose

Lexi-RAG combines **AI retrieval** with **data-security principles**.
Through this project, I aim to strengthen my understanding of:

- 🧩 **RAG architecture:** Connecting embeddings, vector databases, and LLM reasoning
- 🔐 **Data governance:** Enforcing visibility by user role, case, and privilege level
- 🧬 **Encrypted embeddings:** Exploring how encryption influences retrieval accuracy and latency
- ⚙️ **Secure system design:** Building layered databases and metadata-aware search pipelines
- 🧠 **AI infrastructure:** Applying modular design, indexing, and evaluation practices to realistic data workflows

This project reflects my goal to master **AI system design** — going beyond prototypes to explore how intelligent systems stay compliant, reliable, and transparent.

---

## 🚧 Challenges & Expected Learning Outcomes

### 🔒 Data Security & Role-Based Access
- Building a layered database where each user role unlocks deeper information
- Implementing application-level row-level security logic on top of MongoDB and the vector index
- Guaranteeing no cross-case data exposure, even in complex retrieval scenarios

### 🧬 Encrypted Embeddings
- Experimenting with embedding encryption to prevent semantic data leaks
- Learning methods for privacy-preserving retrieval and secure metadata storage
- Measuring trade-offs between speed, accuracy, and confidentiality

### 🧮 Accuracy, Evaluation & Hallucination Control
- Ensuring AI-generated answers remain grounded and verifiable
- Designing evaluation metrics for retrieval precision, recall, and factual correctness
- Including citations and source snippets with every answer
- Minimizing hallucination through careful prompt design and context control

### 🧠 Retrieval & Context Management
- Chunking long, semi-structured legal documents for semantic search
- Combining vector similarity and keyword search (BM25) to improve precision on legal language
- Maintaining traceability by linking each response to its source documents

### 🏗️ System Design & Architecture
- Coordinating multiple user roles with clear permissions
- Connecting MongoDB (metadata) with Qdrant (embeddings)
- Designing an ingestion pipeline that scales as new documents are added

---

## 🧭 Approach

Lexi-RAG follows a layered information model inspired by real legal clearance levels:

| Layer | Access | Example Data |
|------|--------|--------------|
| 1 – Client Layer | Clients & Intake | Case overview, shared documents |
| 2 – Staff Layer | Paralegals & Clerks | Evidence notes, deadlines |
| 3 – Attorney Layer | Lawyers & Partners | Legal strategy, internal memos |
| 4 – Core Intelligence | Partners/System | Encrypted embeddings, analytics |

When a user makes a query:
1. The system checks role and case permissions
2. Retrieves context only from authorized layers
3. Generates an answer with citations linking to original documents

The emphasis is on transparency and trust — AI assists, humans verify.

---

## 🗺️ Roadmap

**Phase 1 — Design & Modeling**
Define data schemas, user roles, and privacy layers

**Phase 2 — Database & Infrastructure Setup**
Implement MongoDB and Qdrant

**Phase 3 — Retrieval Logic**
Build text extraction, chunking, and hybrid semantic search

**Phase 4 — Encryption Layer**
Add encryption for privileged embeddings and benchmark performance

**Phase 5 — Frontend Demo**
Minimal UI with authentication, chat, and citation display

**Phase 6 — Evaluation & Documentation**
Measure retrieval accuracy, groundedness, and privacy guarantees

---

## 📋 Legal

This is a personal portfolio project.

© 2026 Mamadou Kabore. All Rights Reserved.

---

## ✍️ Author
**Mamadou Kabore**
Aspiring AI Engineer focused on building intelligent, secure, and privacy-conscious systems
📍 Ottawa, Canada