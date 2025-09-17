import re
import os
import json
import pandas as pd
from PyPDF2 import PdfReader
from datetime import datetime
from fastapi import HTTPException
from PyPDF2.errors import PdfReadError  

class PDFExtractor:
    def __init__(self, perfiles_dir="perfiles"):
        self.perfiles_dir = perfiles_dir
        
    def cargar_perfil(self, nombre_perfil):
        perfil_path = os.path.join(self.perfiles_dir, f"{nombre_perfil}.json")
        if not os.path.exists(perfil_path):
            raise FileNotFoundError(f"Perfil {nombre_perfil} no encontrado.")
        with open(perfil_path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def procesar(self, pdf_path, patrones):
        try:
            # Leer PDF
            reader = PdfReader(pdf_path)
        except PdfReadError:
            raise HTTPException(status_code=400, detail="Error al leer el archivo PDF. El archivo puede estar corrupto o no ser un PDF válido.")        
        
        texto = "\n".join(page.extract_text() for page in reader.pages)
        
        if not texto.strip():
            raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF. El archivo puede estar protegido o no contener texto seleccionable.")        
        
        # Normalizar con pandas
        lineas = [re.sub(r"\s+", " ", line.strip()) for line in texto.split("\n") if line.strip()]
        df = pd.DataFrame(lineas, columns=["linea"])
        
        #Buscar Datos Generales
        datos_generales = {}
        for campo, patron in patrones.items():
            match = df["linea"].str.extract(patron, expand=False).dropna()
            if not match.empty:
                valor = str(match.iloc[0]).strip()
                if valor:  # solo si no es string vacío
                    if campo == "Nro_Factura":
                    # Normalizar guion → "00003 - 00003231" → "00003-00003231"
                        valor = re.sub(r"\s*[-–]\s*", "-", valor)
                    if campo == "Total" and valor:
                        # Ej: "12.345,67" → "12345.67"
                        valor = valor.replace(".", "").replace(",", ".")
                    try:
                        valor = float(valor)               
                    except ValueError:
                        pass
                    datos_generales[campo] = valor
                    if campo == "Fecha_vencimiento" and valor:
                        valor = valor.replace("-", "/")
                else:
                    datos_generales[campo] = None
            else:
                datos_generales[campo] = None

        
        if not datos_generales:
            raise HTTPException(status_code=422, detail="No se pudo extraer ningún campo con este perfil")
       
       # Extras fijos (depende el cliente)
        datos_generales["Deposito"] = 1
        datos_generales["Fecha_Contable"] = datetime.today().strftime("%d/%m/%Y")
        datos_generales["Comprobante_electronico"] = "S"
        
        return {"datos_generales": datos_generales}

