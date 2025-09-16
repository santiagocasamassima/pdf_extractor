from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile
import os
from extractor import PDFExtractor

app = FastAPI()
extractor = PDFExtractor()


@app.post("/procesar_factura/")
async def procesar_factura_api(
    file: UploadFile = File(...),
    profile: str = "factura"
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        perfil = extractor.cargar_perfil(profile)
        patrones = perfil["patrones"]
        resultado = extractor.procesar(tmp_path, patrones)
    except FileNotFoundError:
        os.remove(tmp_path)
        raise HTTPException(status_code=400, detail="Perfil no encontrado")
    finally:
        os.remove(tmp_path)

    return {"perfil_usado": perfil["name"], "resultado": resultado}
