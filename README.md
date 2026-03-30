<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:24243e&height=220&section=header&text=InfoSphere&fontSize=72&fontColor=ffffff&fontAlignY=38&desc=Biometric+Library+Access+Control+System&descAlignY=58&descSize=18&animation=fadeIn"/>
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:24243e&height=220&section=header&text=InfoSphere&fontSize=72&fontColor=ffffff&fontAlignY=38&desc=Biometric+Library+Access+Control+System&descAlignY=58&descSize=18&animation=fadeIn" width="100%"/>
</picture>

<br/>

<img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square"/>
<img src="https://img.shields.io/badge/Version-1.0-blueviolet?style=flat-square"/>
<img src="https://img.shields.io/badge/Accuracy-95%25-blue?style=flat-square"/>
<img src="https://img.shields.io/badge/Latency-%3C1.8s-orange?style=flat-square"/>
<img src="https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square"/>

<br/><br/>

*Contactless · Secure · Instant · Scalable*

<br/>

</div>

---

## What is InfoSphere?

**InfoSphere** is a full-stack biometric access control system built for modern academic libraries. It eliminates ID cards, RFID tokens, and manual logbooks — replacing them with **real-time facial recognition** that identifies members in under **1.8 seconds**.

The system uses HOG-based face detection and a **128-dimensional deep residual embedding model** to encode and match facial geometry. Built on Python Flask with a MySQL backend, it supports up to **10,000 members** with a clean, responsive web interface.

> *Your face is your library card.*

---

<br/>

## ◈ Feature Highlights

<br/>

**`01` — Biometric Face Verification**

No passwords. No cards. No friction. The system captures a live WebRTC camera stream, extracts a 128-dimensional facial feature vector, and matches it against enrolled members using Euclidean distance — all in under two seconds.

```
Threshold:  distance < 0.6  →  ✅ Access Granted
            distance ≥ 0.6  →  ❌ Access Denied
```

<br/>

**`02` — Automated Member Registration**

Self-service or admin-driven enrollment with instant **6-digit unique ID generation**. Facial encodings are captured live and stored as mathematical vectors — raw images are never retained.

<br/>

**`03` — Admin Control Dashboard**

A full lifecycle management interface for administrators. View registered members, manage access records, delete or update entries, and monitor verification history — protected behind hashed-password authentication and secure sessions.

<br/>

**`04` — Starry Night UI**

An immersive dark-themed interface designed around the project's "Starry Night" aesthetic. Animated backgrounds, real-time verification feedback, and a distraction-free responsive layout optimized for both desktop and tablet.

<br/>

**`05` — Privacy-by-Default Architecture**

No photographs are ever saved. The system stores only abstract numerical vectors representing facial geometry — making it compliant with GDPR data minimization principles from day one.

<br/>

---

## ◈ System Pipeline

```
  Browser (WebRTC)
       │
       │  Live camera frame
       ▼
  Base64 Encode
       │
       │  POST /verify_face
       ▼
  Flask Server
       │
       ├─→  Decode Base64  →  NumPy Array
       │
       ├─→  HOG Face Detection  (Dlib)
       │
       ├─→  128D Feature Encoding  (Deep ResNet)
       │
       ├─→  Load stored encodings from MySQL
       │
       └─→  Euclidean Distance Match
                    │
            ┌───────┴────────┐
          < 0.6            ≥ 0.6
            │                │
       ✅ Verified       ❌ Denied
```

<br/>

---

## ◈ Performance Benchmarks

Tests were conducted across varying lighting conditions, facial angles, and accessory changes (glasses, different expressions).

```
┌─────────────────────────────────────────┐
│                                         │
│   Recognition Accuracy    ████████░  95%│
│   False Acceptance Rate   █░░░░░░░░   3%│
│   False Rejection Rate    █░░░░░░░░   2%│
│   Avg. Processing Time         1.6 sec  │
│   Max Members Supported         10,000  │
│   Optimal Match Threshold          0.6  │
│                                         │
└─────────────────────────────────────────┘
```

### Why HOG over alternatives?

| | Haar Cascades | **HOG + SVM** | CNN |
|--|:--:|:--:|:--:|
| Speed | Very Fast | **Fast** | Moderate |
| Accuracy | 70% | **95%** | 99% |
| Needs GPU | No | **No** | Yes |
| Lighting Tolerance | Low | **Moderate** | High |

> HOG was selected as the ideal balance of speed, accuracy, and zero hardware dependency.

<br/>

---

## ◈ Architecture

InfoSphere follows a clean three-tier MVC structure:

```
  ╔══════════════════════════════╗
  ║      Presentation Layer      ║   HTML · CSS · JS · WebRTC
  ╠══════════════════════════════╣
  ║      Application Layer       ║   Flask · Dlib · face_recognition
  ╠══════════════════════════════╣
  ║         Data Layer           ║   MySQL · Encoded Vectors
  ╚══════════════════════════════╝
```

<br/>

---


<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:24243e,50:302b63,100:0f0c29&height=120&section=footer" width="100%"/>

**Built by Gaya** &nbsp;·&nbsp; Faculty of Computing 

`support@infosphere.com`

*© 2026 InfoSphere*

</div>
