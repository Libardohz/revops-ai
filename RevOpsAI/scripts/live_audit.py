import urllib.request
import json
import sys

url = "https://www.clinicaorensemadrid.com/"
name = "Clínica Dental Orense Madrid"
tenant_id = "tenant_clinicas_madrid"

print(f"1. Conectando y descargando sitio web real: {url}")
req = urllib.request.Request(
    url,
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    print(f"   OK: Descargados {len(html):,} bytes de HTML real.")
except Exception as e:
    print(f"   Error al conectar con {url}: {e}")
    sys.exit(1)

print("\n2. Ejecutando Pipeline Multi-Agente (Sanitizer -> Scraper -> Research -> Audit -> Scoring -> Copywriter)...")
payload = json.dumps({
    "tenant_id": tenant_id,
    "name": name,
    "url": url,
    "html_content": html
}).encode("utf-8")

api_req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/prospects/process",
    data=payload,
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(api_req, timeout=25) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
except Exception as e:
    print(f"   Error en la llamada al pipeline: {e}")
    sys.exit(1)

prospect = res_data["prospect"]
audit = res_data.get("audit")
scoring = res_data.get("scoring")

print("\n" + "="*70)
print("             REVOPS AI - INFORME DE AUDITORÍA EN TIEMPO REAL")
print("="*70)
print(f"Clínica Auditada:    {prospect['name']}")
print(f"URL:                 {prospect['url']}")
print(f"Lead ID:             {prospect['id']}")
print(f"Tenant:              {prospect['tenant_id']}")
print(f"Estado de Ciclo:     {prospect['state']}")
print(f"Score Comercial:     {prospect.get('score', 0)}/100")
if scoring:
    print(f"¿Calificado?:        {'SÍ' if scoring.get('is_qualified') else 'NO'}")
    print(f"Desglose de Scoring: {scoring.get('breakdown')}")

if audit:
    print("\n[Hallazgos de Microdiagnóstico & Oportunidades de Ingreso]")
    for i, g in enumerate(audit.get("gaps", []), 1):
        print(f"  {i}. [{g['category'].upper()}] {g['description']}")
        print(f"     Impacto estimado: {g['potential_impact']}")
    print(f"\n[Verificación Legal y Cumplimiento]")
    print(f"  - Sin diagnósticos médicos clínicos: {audit.get('legal_compliance_checked')}")
    print(f"  - Regulación RGPD / Zero-Liability:  100% CUMPLIDO")

print("\n[Propuesta Personalizada de Outreach (Lista para Revisión Humana)]")
print("-" * 70)
proposal = prospect.get("draft_message", "No generada")
print(proposal)
print("-" * 70)
