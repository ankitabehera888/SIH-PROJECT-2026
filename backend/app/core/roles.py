from enum import Enum


class UserRole(str, Enum):
    """System-wide user roles for Role-Based Access Control (RBAC)."""

    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    NURSE = "NURSE"
    ADMIN = "ADMIN"
    WORKER = "WORKER"

