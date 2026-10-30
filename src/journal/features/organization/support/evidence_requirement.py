from enum import StrEnum


class EvidenceRequirement(StrEnum):
    PRODUCTION_DEPLOYMENT = "production_deployment"
    PUBLISHED_OUTPUT = "published_output"
    VERIFIED_OUTPUT = "verified_output"
    ACCEPTED_OUTPUT = "accepted_output"
