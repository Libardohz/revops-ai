from html.parser import HTMLParser
from pydantic import BaseModel
from RevOpsAI.src.security.sanitizer import InputSanitizer
from RevOpsAI.src.security.pii_scrubber import PIIScrubber

class ScrapeResult(BaseModel):
    url: str
    clean_text: str
    detected_injection: bool
    pii_redacted: bool

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts: list[str] = []
        self._ignore_tag = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._ignore_tag = True
            return

        # Capturar atributos enriquecedores como enlaces href y aria-labels (ej: wa.me, whatsapp)
        for attr, val in attrs:
            if not val:
                continue
            val_lower = val.lower()
            if attr == "href":
                if "wa.me" in val_lower or "whatsapp" in val_lower or "api.whatsapp" in val_lower:
                    self.text_parts.append(f" WhatsApp {val} ")
                elif "tel:" in val_lower or "mailto:" in val_lower:
                    self.text_parts.append(f" {val} ")
            elif "whatsapp" in val_lower:
                self.text_parts.append(" WhatsApp ")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._ignore_tag = False

    def handle_data(self, data: str):
        if self._ignore_tag:
            return
        cleaned = data.strip()
        if cleaned:
            self.text_parts.append(cleaned)

    def get_text(self) -> str:
        return " ".join(self.text_parts)

class SecureWebScraper:
    def __init__(self):
        self.sanitizer = InputSanitizer()
        self.scrubber = PIIScrubber()

    def parse_html(self, url: str, html_content: str) -> ScrapeResult:
        extractor = HTMLTextExtractor()
        extractor.feed(html_content)
        raw_text = extractor.get_text()

        # 1. Sanitizar contra Prompt Injection
        sanitized = self.sanitizer.sanitize(raw_text)

        # 2. Enmascarar datos PII sensibles
        scrubbed = self.scrubber.mask_pii(sanitized.clean_text)

        return ScrapeResult(
            url=url,
            clean_text=scrubbed.scrubbed_text,
            detected_injection=sanitized.detected_injection,
            pii_redacted=len(scrubbed.redacted_fields) > 0
        )
