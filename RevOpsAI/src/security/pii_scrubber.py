import re
from pydantic import BaseModel

class PIIResult(BaseModel):
    scrubbed_text: str
    redacted_fields: list[str]

class PIIScrubber:
    MEDICAL_ID_REGEX = r"\bHC-\d{5,}\b"
    PHONE_REGEX = r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{3,4}\b"

    def mask_pii(self, text: str) -> PIIResult:
        redacted = []
        scrubbed = text
        if re.search(self.MEDICAL_ID_REGEX, scrubbed):
            scrubbed = re.sub(self.MEDICAL_ID_REGEX, "[ID_MEDICO]", scrubbed)
            redacted.append("medical_id")
        if re.search(self.PHONE_REGEX, scrubbed):
            scrubbed = re.sub(self.PHONE_REGEX, "[TELEFONO]", scrubbed)
            redacted.append("phone")
        return PIIResult(scrubbed_text=scrubbed, redacted_fields=redacted)
