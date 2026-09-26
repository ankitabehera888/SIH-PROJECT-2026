# ABDM (Ayushman Bharat Digital Mission) Identity & Provenance Architecture

## 1. Overview
This document outlines the identity resolution, provenance tracking, and data security models connecting the Data Engineering layer to ABDM standards.

---

## 2. Decoupled Identity Architecture

```text
               ┌───────────────────────────────┐
               │    Internal System Patient    │
               │   (UUID: 0d395105-357b-...)   │
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │ analytics.patient_id_map      │
               ├───────────────────────────────┤
               │ internal_patient_id           │
               │ identifier_system             │
               │ identifier_value              │
               │ identifier_type               │
               └───────┬───────────────┬───────┘
                       │               │
        ┌──────────────┘               └──────────────┐
        ▼                                             ▼
┌─────────────────────────┐               ┌─────────────────────────┐
│        FHIR ID          │               │        ABHA ID          │
│ (pat-0d395105-357b-...) │               │    (14-digit National)  │
└─────────────────────────┘               └─────────────────────────┘
```

- **Confidentiality Guard**: Ordinary analytics views and fact tables do not store raw ABHA numbers. Access to `analytics.patient_identifier_map` is restricted to authorized interoperability microservices.

---

## 3. Cryptographic Provenance Architecture

Every exported resource produces a persistent audit trail in `analytics.fhir_provenance`:

```sql
SELECT 
    provenance_key,
    resource_type,
    fhir_resource_id,
    source_table,
    source_record_id,
    pipeline_run_id,
    mapping_version,
    generated_at
FROM analytics.fhir_provenance;
```

This guarantees 100% backward traceability:
1. Which operational row created which FHIR resource?
2. Which pipeline execution generated the record?
3. Which version of the semantic mapping specification was active?
