# 🏛️ Lexi-RAG: A Privacy-First Legal Retrieval System  
**_Personal Project — In Progress_**

---

### 🧠 What Is Lexi-RAG?

Lexi-RAG is a **personal AI engineering project** that explores how **Retrieval-Augmented Generation (RAG)** can power a **law-firm knowledge system** designed around privacy, access control, and real-world security constraints.

Rather than building another general RAG chatbot, this project focuses on **how retrieval systems behave in high-risk environments**, where every query and document must respect **confidentiality, encryption rules, and legal privilege**.

> _Goal: Understand how to design intelligent retrieval systems that are safe, private, and compliant in data-sensitive industries._

---

### ⚖️ Why a Law-Firm Use Case?

Law firms generate enormous volumes of **unstructured information** — contracts, filings, memos, emails, evidence, and invoices — all protected by confidentiality agreements.  
Because this data rarely follows a fixed schema, **MongoDB** is used to store it flexibly while still allowing structured queries.

Lexi-RAG envisions a secure AI assistant that helps each role differently:
- **Lawyers and partners:** Search legal clauses, filings, and case summaries.  
- **Paralegals and clerks:** Organize evidence and deadlines efficiently.  
- **Intake admins:** Manage client onboarding and schedules.  
- **Clients:** View their own case status and shared materials only.  

Everything operates under strict privacy layers to preserve legal privilege.

---

### 💡 Project Purpose

Lexi-RAG is a **learning-driven project** that combines **AI retrieval** with **data security principles**.  
Through it, I aim to deepen my understanding of:

- 🧩 **RAG architecture:** Connecting embeddings, vector databases, and LLM reasoning.  
- 🔐 **Data governance:** Enforcing visibility by user role, case, and privilege level.  
- 🧬 **Encrypted embeddings:** Studying how encryption affects retrieval accuracy and system performance.  
- ⚙️ **Secure system design:** Building layered databases and metadata-aware search pipelines.  
- 🧠 **AI infrastructure:** Practicing modular design, indexing, and evaluation in realistic workflows.  

This project is part of my journey to master **AI system design** — going beyond prototypes to explore how intelligent systems stay compliant and trustworthy.

---

## 🚧 Challenges & Expected Learning Outcomes

Building Lexi-RAG involves multiple interconnected challenges that mirror real enterprise systems:

### 🔒 Data Security & Role-Based Access
- Building a **layered database** where each user role unlocks deeper information.  
- Implementing application-level **Row-Level Security logic** for MongoDB and the vector index.  
- Guaranteeing **no cross-case data exposure**, even in complex searches.

### 🧬 Encrypted Embeddings
- Experimenting with **embedding encryption** to prevent semantic data leaks.  
- Learning techniques for **privacy-preserving retrieval** and secure metadata storage.  
- Measuring the trade-off between **speed, accuracy, and confidentiality**.

### 🧠 Retrieval & Context Management
- Chunking long, semi-structured legal documents for semantic search.  
- Combining **vector similarity** and **keyword search (BM25)** for robust accuracy.  
- Returning **traceable results** with clear citations to original documents.

### 🏗️ System Design & Architecture
- Coordinating multi-role access logic (lawyer, paralegal, admin, client).  
- Linking **MongoDB** for document metadata and **Qdrant** for vector embeddings.  
- Designing an ingestion pipeline that can scale as new data arrives.

### 📚 Key Learning Goals
- Master **embedding models**, **vector databases**, and **hybrid retrieval**.  
- Strengthen **system-design thinking** and **secure data architecture skills**.  
- Practice evaluating AI systems where **governance and intelligence intersect**.

---

## 🧭 Approach

Lexi-RAG follows a **layered information model**, similar to real legal clearance levels:

| Layer | Access | Example Data |
|--------|---------|--------------|
| **1 – Client Layer** | Clients & Intake | Case overview, shared documents |
| **2 – Staff Layer** | Paralegals & Clerks | Evidence notes, deadlines |
| **3 – Attorney Layer** | Lawyers & Partners | Legal strategy, internal memos |
| **4 – Core Intelligence** | Partners/System | Encrypted embeddings, analytics |

Each query checks the user’s role, filters by permitted layers, and searches only within authorized data scopes.  
Higher-sensitivity layers use **encrypted embeddings**, decryptable only by privileged roles.  

This approach creates a **hierarchy of visibility**, teaching me to design retrieval systems that balance intelligence, performance, and confidentiality.

---

## 🗺️ Roadmap

**Phase 1 — Design & Modeling**  
Define data schemas, user roles, and privacy layers.  

**Phase 2 — Database & Infrastructure Setup**  
Implement MongoDB for unstructured data and Qdrant for vectors.  

**Phase 3 — Retrieval Logic**  
Build text extraction, chunking, and hybrid search with metadata filtering.  

**Phase 4 — Encryption Layer**  
Add client- or server-side encryption for privileged embeddings; benchmark results.  

**Phase 5 — Frontend Demo**  
Develop a minimal interface with authentication, chat view, and citation display.  

**Phase 6 — Evaluation & Documentation**  
Measure retrieval accuracy, privacy strength, and overall system performance.

---

### 🧾 License
MIT License — free for educational and research purposes.

---

### ✍️ Author
**Mamadou Kabore**  
_Aspiring AI Engineer focused on building intelligent, secure, and privacy-conscious systems._  
📍 Ottawa, Canada
