from fastapi import FastAPI, UploadFile, File
from pypdf import PdfReader
import pandas as pd
import re
import os
import json
from datetime import datetime
import tempfile

app = FastAPI()

def procesar_factura(pdf_path):
    # Leer PDF
    if not os.path.exists(pdf_path):
        print(f"⚠️ No se encontró el archivo en {pdf_path}")
        return
    
    reader = PdfReader(pdf_path)
    texto = "\n".join(page.extract_text() for page in reader.pages)

    # Normalizar con pandas
    lineas = [re.sub(r"\s+", " ", line.strip()) for line in texto.split("\n") if line.strip()]
    df = pd.DataFrame(lineas, columns=["linea"])

    # Patrones básicos
    patrones = {
        "Fecha": r"\bFecha[:\s]+(\d{2}/\d{2}/\d{4})",
        "Nro_Factura": r"(?:Factura|FACTURA|FAA)\s*(?:N°|No|Nº)?\s*([\d\-]+)",
        "CUIT": r"CUIT[:\s]*([\d\-]+)",
        "Total": r"TOTAL\s*\$?\s*([\d\.,]+)",
        "CAE": r"CAE[:\s]*([\d]+)",
        "Fecha_vencimiento": r"\bFecha Vencimiento[:\s]+(\d{2}/\d{2}/\d{4})",
        "Condiciones_Venta": r"Condiciones(?: de (?:Venta|Pago))?[:\s]*(.+)"
    }

    datos_generales = {}
    for campo, patron in patrones.items():
        match = df["linea"].str.extract(patron, expand=False).dropna()
        if not match.empty:
            datos_generales[campo] = match.iloc[0]
    
    # Proveedor → asumimos que es la primera línea con mayúsculas o "S.A.", "SRL", etc.
    proveedor = df["linea"][df["linea"].str.contains(r"S\.A\.|S\.R\.L|S\.A|SRL|Ltda", case=False, regex=True)]
    if not proveedor.empty:
        datos_generales["Proveedor"] = proveedor.iloc[0]
    else:
        # fallback → primera línea del PDF
        datos_generales["Proveedor"] = df.iloc[0]["linea"]

    idx = df.index[df["linea"].str.contains(r"Condiciones\s*de\s*Venta", case=False, regex=True)]
    if not idx.empty:
        start = idx[0]
        condiciones_texto = []
        for i in range(start, len(df)):
            linea = df.loc[i, "linea"].strip()
            if re.search(r"(TOTAL|CAE|Factura|CUIT)", linea, re.IGNORECASE):  # cortamos en otra sección
                break
            condiciones_texto.append(linea)

        condiciones_texto = " ".join(condiciones_texto)
        match_plazo = re.search(r"\d+\s*d[ií]as", condiciones_texto, re.IGNORECASE)
        if match_plazo:
            datos_generales["Condiciones_Venta"] = match_plazo.group(0)  # ej: "60 días"
    
    # ➕ Valor fijo de Depósito
    datos_generales["Deposito"] = 1
    # ➕ Fecha Contable = fecha del día
    datos_generales["Fecha_Contable"] = datetime.today().strftime("%d/%m/%Y")

    # Valor fijo de Comprante electrónico
    datos_generales["Comprobante_electronico"] = "S"

    #-------------------------------
    # Buscar Bonificación en tabla
    # -------------------------------
    # Buscamos la línea que contiene BON en el header
    bon_idx = df.index[df["linea"].str.contains(r"\bBON", case=False, regex=True)]
    if not bon_idx.empty:
        # Encabezado que contiene BON
        header_line = df.loc[bon_idx[0], "linea"]
        header_cols = re.split(r"\s{2,}", header_line)

        # Posición de la columna BON
        try:
            pos_bon = next(i for i, col in enumerate(header_cols) if "BON" in col.upper())

            # Buscar primera fila de ítems después del encabezado
            for i in range(bon_idx[0] + 1, len(df)):
                first_item_line = df.loc[i, "linea"]
                item_cols = re.split(r"\s{2,}", first_item_line)
                if len(item_cols) > pos_bon:  # aseguramos que hay columna en esa posición
                    bonificacion_val = item_cols[pos_bon]

                    # Validar que sea un número (ej. 10, 10.00, 20,80)
                    if re.match(r"^\d+[.,]?\d*$", bonificacion_val):
                        datos_generales["Bonificacion"] = bonificacion_val.replace(",", ".")
                    break
        except StopIteration:
            pass
    return {"datos_generales": datos_generales}

@app.post("/procesar_factura/")
async def procesar_factura_api(file: UploadFile = File(...)):
    # Guardamos el PDF temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Procesamos
    resultado = procesar_factura(tmp_path)

    # Borramos archivo temporal
    os.remove(tmp_path)

    return resultado


