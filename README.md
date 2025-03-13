# **Distributed Password Cracker**

A fully distributed system for cracking MD5 hashes of phone numbers (`05X-XXXXXXX`).
The project utilizes **FastAPI**, **RabbitMQ**, **Redis**, and a set of **asynchronous workers** to efficiently distribute and process hash-cracking tasks.

---

## **Features**
- Distributed Hash Cracking – Work is distributed among multiple workers for parallel processing.
- Scalable Architecture – Can dynamically scale minion workers and result processors.
- Task Queueing with RabbitMQ – Ensures efficient task distribution and load balancing.
- Redis-based Status Storage – Enables fast retrieval of task statuses.
- Persistent Storage – Redis and RabbitMQ use **PVC (Persistent Volumes)** to prevent data loss.
- Fault-Tolerant System – Implements retry mechanisms and exception handling for stability.
- Fully Containerized with Docker – Just **pull, run, and deploy** with `docker-compose`.

---

## **Installation & Setup**
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/Yardenl22/distributed-password-cracker.git
cd distributed-password-cracker
```

### **2️⃣ Build & Start the System**
```bash
docker-compose up --build
```
This will:
- Start **FastAPI** on `http://localhost:8080`
- Initialize **RabbitMQ** and **Redis**
- Run **5 minion workers** and **2 result processors**

### **3️⃣ Check Running Containers**
```bash
docker ps
```

### **4️⃣ Access the API**
- Open **`http://localhost:8080/docs`** in your browser.

### **5️⃣ Submit a Hash for Cracking**
```bash
curl -X POST "http://localhost:8080/upload_hashes" \
     -H "Content-Type: application/json" \
     -d '{"hashes": [
            "1d0b28c7e3ef0ba9d3c04a4183b576ac",
            "0da74e79f730b74d0b121f6817b13eac",
            "4fcaeb8f267533389d1ce65053c631df",
            "0eecc2b2ff6160bc7c6d9d601f08529a",
            "1a1674fc1f2ce010f161b4cd1ad80939"
          ]
        }'
```

### **6️⃣ Check Task Status**
```bash
curl -X GET "http://localhost:8080/task_status/your_task_id"
```

### **7️⃣ Access RabbitMQ UI**
- Open **`http://localhost:15672`**
- Username: `user`, Password: `password`

### **8️⃣ Scaling Workers**
Need more power? Scale workers dynamically:
```bash
docker-compose up --scale minion=10
```
This increases minion workers from 5 to 10.

---

## **API Usage**

| **Method** | **Endpoint**             | **Description** |
|-----------|--------------------------|-----------------|
| **POST**  | `/upload_hashes`, `/upload_file`       | Submit MD5 hashes for cracking. |
| **GET**   | `/task_status/{task_id}` | Retrieve the status of a submitted task. |

---

## **Code Architecture & Design Decisions**

The system follows a **modular and distributed design** to efficiently distribute computational workloads across multiple workers. 
The **FastAPI master server** manages tasks, while **minion workers** handle hash-cracking in parallel.

### **Key Code Components**

#### **Storage System**
The `storage` module manages task result storage. It currently supports JSON-based storage but is designed for easy expansion to databases like MongoDB.

- **`BaseStorage` (Abstract Class)** – Defines required storage operations.
- **`JSONStorage`** – Implements persistent storage in JSON format.
- **`StorageFactory`** – Dynamically selects the storage backend.

#### **Application Runner**
The system is designed to run as a **distributed microservices architecture**:
- `master/app.py` – Starts the FastAPI master server.
- `minion/worker.py` – Listens to RabbitMQ and processes tasks.
- `result_processor.py` – Receives and stores cracked passwords.

#### **Exception Handling**
- **Retries & Graceful Failures** – Implements retries for failed tasks.

---

## **Future Enhancements**
- Task Status Updates in Redis – Add live progress tracking for each hash-cracking task.
- Database Integration – Store cracked passwords in a relational DB instead of JSON.
- Advanced Load Balancing – Optimize worker distribution based on real-time load metrics.

---

🚀 **This system is ready for deployment and can easily scale with additional minion workers!**
