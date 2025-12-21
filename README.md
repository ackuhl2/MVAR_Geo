# MVAR-Geo: Multidimensional Visualization of Association Rules for Geographic Data

MVAR-Geo is a prototype tool for the extraction and spatial visualization of Association Rules (ARM) in geographic contexts. It bridges the gap between traditional data mining and geographic information systems.

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Installation and Execution](#-installation-and-execution)
- [Data Sources](#-data-sources)

## 🚀 Project Overview
The tool transforms abstract association rules into observable spatial phenomena, enabling the identification of:
- **Spatial Polarization:** Such as North-South divides in health data.
- **Geographic Enclaves:** Localized anomalies in electoral patterns.
- **Multiscale Navigation:** Transitions between State, Micro-region, and Municipal levels.

## ✨ Key Features
- **Interactive Maps:** Layers for different administrative levels.
- **Chromatic Transitions:** Visual representation of temporal data evolution.
- **ARM Filtering:** Dynamic filters based on support, confidence, and lift.

## 🛠️ Requirements
- **Environment:** Java (JRE/JDK) v1.8 or higher.
- **Framework:** Grails / Apache Tomcat.
- **Browser:** Modern browser (Chrome/Firefox) for map rendering.

## 🔧 Installation
1. **Clone:** `git clone https://github.com/ackuhl2/MVAR-Geo.git`
2. **Build:** `./gradlew assemble`
3. **Run:** `java -jar build/libs/mvar-core-0.1.war`
4. **Access:** `http://localhost:8080/MVAR-Geo`

## 📊 Data Sources
- **COVID-19 (MS):** 2020-2022 triennium (485 MB).
- **Elections (TSE):** 2018/2022 second round (2.8 GB).
- **Tourism (Data.Rio):** 2.67M foreign connections (2020-2021).

---
**License:** MIT | **Contact:** ackuhl2 via GitHub.
