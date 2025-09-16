from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile
import os
from extractor import PDFExtractor

app = FastAPI()
extractor = PDFExtractor()

@app.get("/perfiles/")
def listar_perfiles():
    perfiles_dir = "perfiles"
    perfiles = [f.replace(".json", "") for f in os.listdir(perfiles_dir) if f.endswith(".json")]
    return {"perfiles_disponibles": perfiles}


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
        raise HTTPException(status_code=404, detail=f"Perfil '{profile}' no encontrado")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return {"perfil_usado": perfil["name"], "resultado": resultado}


