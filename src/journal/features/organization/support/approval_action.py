from enum import StrEnum


class ApprovalAction(StrEnum):
    """An action that always waits for the user's approval, whoever asks for it (ARCHITECTURE.md 12.1)."""

    PRODUCTION_DEPLOYMENT = "production_deployment"
    DESTRUCTIVE_DATA_CHANGE = "destructive_data_change"
    FINANCIAL_TRANSACTION = "financial_transaction"
    INVOICE_CORRECTION = "invoice_correction"
    CONTRACT_CHANGE = "contract_change"
    PRIVACY_DECISION = "privacy_decision"
    LEGAL_DECISION = "legal_decision"
    SECURITY_DECISION = "security_decision"
    DATA_BREACH_DECISION = "data_breach_decision"
    PEOPLE_ACTION = "people_action"
    EMPLOYMENT_TERMS_ACTION = "employment_terms_action"
    CUSTOMER_LIABILITY_COMMITMENT = "customer_liability_commitment"
    VEHICLE_TRACKER_DRIVER_IMPACT = "vehicle_tracker_driver_impact"
