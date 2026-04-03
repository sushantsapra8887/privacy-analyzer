"""Configuration for the privacy policy compliance analyzer."""

# Risk score added per missing required clause
MISSING_REQUIRED_CLAUSE_PENALTY = 1.5

# Risk score added per missing optional clause
MISSING_OPTIONAL_CLAUSE_PENALTY = 0.5

# Base risk score when all required clauses are present
BASE_RISK_SCORE = 1

# Maximum risk score cap
MAX_RISK_SCORE = 10

# Minimum risk score floor
MIN_RISK_SCORE = 1

# Minimum policy text length (characters) to consider valid
MIN_POLICY_LENGTH = 50
