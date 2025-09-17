from PyPDF2 import PdfReader
import re

# 👉 Cambiá esta ruta por la de tu factura real
pdf_path = "factura.pdf"

# 1) Leer todas las páginas
reader = PdfReader(pdf_path)
for i, page in enumerate(reader.pages):
    raw = page.extract_text() or ""
    print(f"\n--- PAGINA {i+1} ---")
    print(repr(raw))  # repr() muestra espacios, saltos de línea, etc.

# 2) Filtrar líneas con "vto", "venc" o fechas dd/mm/yyyy
texto = "\n".join((page.extract_text() or "") for page in reader.pages)
lineas = texto.splitlines()

print("\n=== LINEAS CANDIDATAS ===")
for idx, l in enumerate(lineas):
    if (re.search(r'(?i)(vto|venc|vence|vencimiento)', l) or
        re.search(r'\b\d{2}[-/]\d{2}[-/]\d{4}\b', l)):
        print(f"[{idx}] {repr(l)}")
