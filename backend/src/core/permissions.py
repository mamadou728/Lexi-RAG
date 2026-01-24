# src/utils/permissions.py
from typing import List
from models.auth import SystemRole

# Sensitivity levels defined as strings to match your Qdrant payload
ALLOWED_LEVELS = {
    SystemRole.PARTNER:   ["public", "internal", "privileged", "discovery"],
    SystemRole.ASSOCIATE: ["public", "internal", "privileged", "discovery"],
    SystemRole.STAFF:     ["public", "internal"], # Staff cannot see Privileged
    SystemRole.CLIENT:    ["public"]              # Clients only see Public
}

def get_allowed_sensitivities(role: SystemRole) -> List[str]:
    return ALLOWED_LEVELS.get(role, [])