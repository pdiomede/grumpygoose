# 🪿 GOOSE
**Governance Oversight & Operational Speed Evaluator**

---

## 📋 Overview

GOOSE monitors and analyzes the responsiveness of The Graph Council members across Snapshot proposals and Safe multisig transactions. A lightweight dashboard focused on core metrics: time to quorum, individual response times, and participation rates.

---

## 🎯 Objectives

- ⏱️ Track how long it takes to reach **6 of 10 signatures** (quorum)
- 👤 Measure **individual voter/signer response times**
- 🏆 Identify the **top 10 most active council members** by participation rate
- 📊 Provide **historical visibility** into governance efficiency

---

## 📡 Data Sources

### 1️⃣ Snapshot Proposals
- **Platform:** The Graph Council space
- **Space ID:** `council.graphprotocol.eth`
- **URL:** [https://snapshot.box/#/s:council.graphprotocol.eth](https://snapshot.box/#/s:council.graphprotocol.eth)

### 2️⃣ Safe Multisig Transactions
- **Network:** Arbitrum One
- **Address:** `0x8C6de8F8D562f3382417340A6994601eE08D3809`
- **URL:** [View on Safe](https://app.safe.global/transactions/queue?safe=arb1:0x8C6de8F8D562f3382417340A6994601eE08D3809)

---

## 📈 Core Metrics

### ⏱️ Time to Quorum
- Duration from proposal/transaction creation to **6th signature**
- Statistics: Average, median, min, max
- Breakdown by platform (Snapshot vs Safe)

### ⚡ Individual Response Times
- Time from creation to each member's vote/signature
- Average response time per member
- Comparative rankings

### 🏆 Participation Rate
- Rank council members by participation rate
- Percentage of proposals/transactions each member voted on or signed
- Total votes/signatures count per member

---

## 🎨 Dashboard Features

### 1. Summary Cards
Quick overview of total proposals, transactions, votes, and active members

### 2. Time to Quorum Metrics
- **All Platforms:** Combined statistics
- **Snapshot:** Platform-specific metrics
- **Safe Multisig:** Platform-specific metrics

### 3. Leaderboard
Top 10 council members displaying:
- **Rank** (1-10)
- **Address** with vote counts
- **Participation Rate** percentage
- **Average Response Time**

---

## 🛠️ Technical Requirements

- ✅ Data collection from **Snapshot GraphQL API**
- ✅ Data collection from **Safe Transaction Service API**
- ✅ Historical data backfill capability
- ✅ **SQLite** database for metrics storage
- ✅ Static dashboard (manual refresh, no real-time)
- ✅ **Python** backend with **Flask**
- ✅ Pure **HTML/CSS/JavaScript** frontend (no frameworks)
- ✅ Follows **The Graph brand guidelines**

---

## ✅ Success Criteria

- ✓ Accurate tracking of all votes and signatures
- ✓ Clean, readable visualization of core metrics
- ✓ Historical data available for meaningful analysis
- ✓ Clear identification of top 10 most active members
- ✓ Dashboard loads in < 2 seconds
- ✓ Brand-compliant design
