import re
from pydantic import BaseModel

class SanitizedContent(BaseModel):
    clean_text: str
    detected_injection: bool

class InputSanitizer:
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"disregard\s+prior\s+rules",
        r"system\s*:\s*you\s+are",
        r"output\s+admin\s+password",
        r"bypass\s+guardrails"
    ]

    def sanitize(self, text: str) -> SanitizedContent:
        detected = False
        clean = text
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, clean, re.IGNORECASE):
                detected = True
                clean = re.sub(pattern, "[AMENAZA_BLOQUEADA]", clean, flags=re.IGNORECASE)
        return SanitizedContent(clean_text=clean.strip(), detected_injection=detected)
