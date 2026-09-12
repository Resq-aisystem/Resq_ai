# RESQ-AI Emergency Priority & Vulnerable Location Assessment Report

**Project**: RESQ-AI — Disaster Early Warning & Rescue Intelligence Platform  
**Observation Date**: 2026-09-11  
**Scope**: 728 Districts across India  

---

## Executive Summary

The RESQ-AI Emergency Priority Scoring Engine provides operational ranking and situational decision-support for disaster response teams. While the **Production Risk Inference Engine** measures current situational hazard risk driven by observed weather patterns, the **Emergency Priority Engine** combines situational risk with physical terrain flood susceptibility, hydrological vulnerability, historical flood recurrence, and multi-hazard exposure priors to answer:

> *"If multiple districts have elevated disaster risk, which districts should emergency teams consider first for operational attention and resource positioning?"*

> [!IMPORTANT]
> **Operational Wording & Distinction**:
> The ranked districts in this report represent the **highest-priority districts according to the RESQ-AI decision-support score**. They are **NOT** claimed as confirmed active disaster zones or real-world emergency deployments.

---

## Priority Level Distribution

| Operational Priority Level | Threshold Range | District Count | Percentage | Primary Operational Action |
| :--- | :--- | :--- | :--- | :--- |
| **P1 — Immediate Attention** | Priority Score $\ge 70.0$ | **9** | 1.24% | Immediate situational review & resource mobilization watch |
| **P2 — High Priority** | $50.0 \le \text{Score} < 70.0$ | **173** | 23.76% | Active monitoring & team standby |
| **P3 — Monitor / Prepare** | $30.0 \le \text{Score} < 50.0$ | **454** | 62.36% | Pre-positioning review & routine watch |
| **P4 — Routine Monitoring** | Score $< 30.0$ | **92** | 12.64% | Baseline monitoring |

- **Total Districts Processed**: **728 / 728** (100% geographic grid coverage)
- **Priority Score Bounds**: Min = `22.34`, Max = `74.44`, Mean = `42.49`

---

## Top 20 Priority Districts (Decision-Support Ranking)

| Rank | District | State | Risk Score | Risk Level | Priority Score | Priority Level | Key Vulnerability Flags |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | ALIPURDUAR | WEST BENGAL | 70.51 | HIGH | **74.44** | **P1** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `HIGH_HYDROLOGICAL_VULNERABILITY`, `MULTI_HAZARD_HISTORY` |
| **2** | DARJEELING | WEST BENGAL | 67.04 | HIGH | **74.23** | **P1** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `HIGH_HYDROLOGICAL_VULNERABILITY`, `MULTI_HAZARD_HISTORY` |
| **3** | KASARGOD | KERALA | 58.64 | HIGH | **73.37** | **P1** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `HIGH_HYDROLOGICAL_VULNERABILITY`, `MULTI_HAZARD_HISTORY` |
| **4** | NAGAPATTINAM | TAMIL NADU | 59.22 | HIGH | **71.19** | **P1** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `MULTI_HAZARD_HISTORY` |
| **5** | KOTTYAM | KERALA | 53.66 | MODERATE | **71.13** | **P1** | `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `HIGH_HYDROLOGICAL_VULNERABILITY`, `MULTI_HAZARD_HISTORY` |
| **6** | COIMBATORE | TAMIL NADU | 57.12 | HIGH | **70.69** | **P1** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `MULTI_HAZARD_HISTORY` |
| **7** | KHERI | UTTAR PRADESH | 56.90 | HIGH | **70.54** | **P1** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `MULTI_HAZARD_HISTORY` |
| **8** | N.C HILLS | ASSAM | 58.64 | HIGH | **70.45** | **P1** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `HIGH_HYDROLOGICAL_VULNERABILITY`, `MULTI_HAZARD_HISTORY` |
| **9** | NUAPARHA | ODISHA | 61.14 | HIGH | **70.16** | **P1** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `MULTI_HAZARD_HISTORY` |
| **10** | BANGLORE URBAN | KARNATAKA | 57.14 | HIGH | **68.98** | **P2** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `MULTI_HAZARD_HISTORY` |
| **11** | BAPATLA | ANDHRA PRADESH | 56.95 | HIGH | **68.89** | **P2** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `MULTI_HAZARD_HISTORY` |
| **12** | YSR DISTRICT | ANDHRA PRADESH | 56.95 | HIGH | **68.89** | **P2** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `MULTI_HAZARD_HISTORY` |
| **13** | BHABUA | BIHAR | 60.50 | HIGH | **68.88** | **P2** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `MULTI_HAZARD_HISTORY` |
| **14** | ARIYALUR | TAMIL NADU | 57.05 | HIGH | **68.84** | **P2** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `MULTI_HAZARD_HISTORY` |
| **15** | WEST SINGHBHUM | JHARKHAND | 54.89 | MODERATE | **68.76** | **P2** | `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `HIGH_HYDROLOGICAL_VULNERABILITY`, `MULTI_HAZARD_HISTORY` |
| **16** | NTR DISTRICT | ANDHRA PRADESH | 56.38 | HIGH | **68.63** | **P2** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `MULTI_HAZARD_HISTORY` |
| **17** | KARBI ANALOG | ASSAM | 54.01 | MODERATE | **68.36** | **P2** | `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `HIGH_HYDROLOGICAL_VULNERABILITY`, `MULTI_HAZARD_HISTORY` |
| **18** | PACHIM CHAMPARAN | BIHAR | 57.14 | HIGH | **68.36** | **P2** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `MULTI_HAZARD_HISTORY` |
| **19** | MALDA | WEST BENGAL | 54.83 | MODERATE | **68.25** | **P2** | `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `HIGH_HYDROLOGICAL_VULNERABILITY`, `MULTI_HAZARD_HISTORY` |
| **20** | KALLAKURICHI | TAMIL NADU | 55.67 | HIGH | **68.22** | **P2** | `HIGH_CURRENT_RISK`, `HIGH_FLOOD_SUSCEPTIBILITY`, `HIGH_HISTORICAL_FLOOD_RECURRENCE`, `MULTI_HAZARD_HISTORY` |

---

## Risk vs. Priority Comparison

The distinction between situational hazard risk and operational priority is clearly demonstrated by districts such as **KOTTYAM** and **WEST SINGHBHUM**:

- **KOTTYAM (Rank 5)**: Has a `MODERATE` situational risk score of **53.66**, but receives an immediate operational priority score of **71.13 (P1)**. This elevation occurs because Kottyam exhibits extreme terrain flood susceptibility (GFSM score 4.8/5.0), high historical flood recurrence (IFI recurrence rate > 3.5 events/decade), and high hydrological runoff potential.
- **ALIPURDUAR (Rank 1)**: Combines both `HIGH` situational risk (**70.51**) and top-tier vulnerability priors to achieve the highest priority score (**74.44, P1**).

---

## Evidence Quality & Feature Integrity

- **Evidence Quality**: **100% HIGH** (728 / 728 districts have complete multi-layer data coverage across IMD, GFSM, CAMELS, IFI, and NASA GDIS).
- **Target Leakage Strict Audit**: Zero target-derived variables (`ifi_dfsi_score`, `ifi_flooded_area_pct`, `target_flooded_area_pct`, `target_risk_level`, fatalities, injured) were used as priority predictors.
- **Vulnerability Flags**: Generated strictly from verified dataset features. Unverified infrastructure flags (hospitals, schools, bridges, roads) were excluded due to lack of source datasets.

---

## Operational Limitations

1. **No Real-Time Infrastructure Data**: The engine evaluates physical and historical exposure priors; it does not track real-time hospital capacities, school locations, or road closures.
2. **Decision-Support Scope**: All scores provide relative operational ranking across districts to support resource allocation and decision-making; they do not dictate emergency command directives.
