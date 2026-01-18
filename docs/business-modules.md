# Business Modules

This document describes the main business areas implemented in ElanelSystem. Names and workflows may evolve.

## 1) Sales Management

Purpose: track and organize sales operations in a structured and auditable way.

Typical capabilities:

- Register sales operations and their relevant attributes.
- Relate sales records to internal users
- Support status changes (cancelled, awarded) when applicable.
- Provide filters to search operations by date ranges, agency, or products.

## 2) Commissions / Earnings Logic

Purpose: apply business rules to calculate commissions (or similar earnings) based on sales records.

Typical capabilities:

- Associate commission rules or rates to specific sales or categories.
- Calculate totals based on the configured rules.
- Allow supervised correction when a record needs manual adjustment.

## 3) Payroll / Liquidations

Purpose: consolidate and generate liquidation periods for staff and/or collaborators.

Typical capabilities:

- Define liquidation periods (month/year, or custom ranges).
- Consolidate records for the period and compute totals.
- Support review workflows before final approval.
- Keep outputs consistent for accounting and operational checks.

## 4) Staff & User Management

Purpose: manage internal users and how they interact with operational workflows.

Typical capabilities:

- Create and manage users.
- Keep historical consistency the personnel history of each agency.
- Maintain basic profile and operational metadata.
- Support onboarding/offboarding through role changes or deactivation.

## 5) Roles & Permissions (RBAC-like behavior)

Purpose: ensure internal tools are protected and actions match user responsibilities.

Typical capabilities:

- Restrict sensitive areas (financial edits, payroll approval, admin tools).
- Define roles for different responsibilities (e.g., admin, supervisor, operator).
- Keep permissions consistent across UI actions and backend validations.

## 6) Financial Operations

Purpose: support internal financial tracking and operational consistency.

Typical capabilities:

- Track financial records related to operations (income/expenses or internal categories).
- Provide visibility and reporting for decisions.
- Support basic reconciliation workflows when required.

## 7) Reporting & Exports

Purpose: reduce manual work by providing structured operational and financial outputs.

Typical capabilities:

- Summary reports by period, user, category, or operational unit.
- Detailed views to audit why totals result in a given amount.
- Export capabilities where needed to integrate with external workflows.
