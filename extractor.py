import re
import os
import json
import pandas as pd
from PyPDF2 import PdfReader
from datetime import datetime

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

        # Leer PDF
        reader = PdfReader(pdf_path)
        texto = "\n".join(page.extract_text() for page in reader.pages)
        
        # Normalizar con pandas
        lineas = [re.sub(r"\s+", " ", line.strip()) for line in texto.split("\n") if line.strip()]
        df = pd.DataFrame(lineas, columns=["linea"])
        
        #Buscar Datos Generales
        datos_generales = {}
        for campo, patron in patrones.items():
            match = df["linea"].str.extract(patron, expand=False).dropna()
            if not match.empty:
                datos_generales[campo] = match.iloc[0].values[0]
            else:
                datos_generales[campo] = None
        
       # Extras fijos (depende el cliente)
        datos_generales["Deposito"] = 1
        datos_generales["Fecha_Contable"] = datetime.today().strftime("%d/%m/%Y")
        datos_generales["Comprobante_electronico"] = "S"
        
        return {"datos_generales": datos_generales}

