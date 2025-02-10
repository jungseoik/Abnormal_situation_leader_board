## **1. Overview**  

The **Leaderboard** system requires structured management of models and benchmark sets due to continuous submission requests. The folder structure must be **dynamically adaptable** while maintaining **logical dependencies**:  

- **Models and vectors** are interdependent.  
- **Benchmarks and datasets** are interdependent.  

This document outlines the **initial structure provided by the data team** and the **restructured folder hierarchy** designed to accommodate scalability and maintainability.  

---

## **2. Initial Structure (Provided by the Data Team)**  

The initial folder structure follows a simple categorization:  

```
📂 /Leaderboard
 ├── 📁 assets
 │   ├── 📁 {category name}
 │   │   ├── 📼 {video name}.mp4
 │   │   ├── 📜 {video name}.json
 │   ├── 📁 {category name2}
 │   │   ├── 📼 {video name1}.mp4
 │   │   ├── 📜 {video name1}.json
```
- **Assets** are categorized directly under `category name`.  
- Each category contains **videos (`.mp4`)** and **metadata (`.json`)** files.  

---

## **3. Restructured Folder Hierarchy**  

To support **benchmarking, model management, and scalable organization**, the folder structure is **redesigned** as follows:  

```
📂 /Leaderboard
 ├── 📁 assets
 │   ├── 📁 {benchmark name}
 │   │   ├── 📁 dataset
 │   │   │   ├── 📁 {category name}
 │   │   │   │   ├── 📼 {video name}.mp4
 │   │   │   │   ├── 📜 {video name}.json
 │   │   ├── 📁 CFG
 │   │   │   ├── 📜 {prompt cfg name}.json
 │   │   ├── 📁 models
 │   │   │   ├── 📁 {model name}
 │   │   │   │   ├── 📁 CFG
 │   │   │   │   │   ├── 📁 {prompt cfg name}
 │   │   │   │   │   │   ├── 📁 alarm
 │   │   │   │   │   │   ├── 📁 metric
 │   │   │   │   ├── 📁 vector
 │   │   │   │   │   ├── 📁 text
 │   │   │   │   │   ├── 📁 video
```

---

## **4. Key Structural Enhancements**  

### 📌 **Benchmarks & Dataset Organization**  
- Each **benchmark** now has a dedicated folder (`{benchmark name}`) under `assets`.  
- `dataset/` subfolder organizes **video files and metadata** under specific **categories**.  

### 📌 **Configuration (CFG) Management**  
- **CFG (`Configuration`) folder** stores **prompt configuration files** relevant to each benchmark.  

### 📌 **Model Structuring**  
- Each **model** has its dedicated subfolder within the benchmark’s `models/` directory.  
- Inside each model folder:  
  - `CFG/` manages **prompt-specific alarm and metric configurations**.  
  - `vector/` stores **text and video-based vector representations**.  

---
