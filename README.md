¡Listo! 🚀 Acá tenés el **README.md** completo, limpio y preparado para subir directamente a tu repositorio en GitHub:

---


# PDF Extractor API

Microservicio modular en **FastAPI** para extraer datos de facturas PDF y convertirlos a JSON.  
Diseñado para ser extensible mediante **perfiles JSON** que contienen expresiones regulares configurables por tipo de documento.

---

## 🚀 Instalación

1. **Clonar el repositorio**

   git clone https://github.com/tu-usuario/pdf-extractor.git
   cd pdf-extractor


2. **Crear un entorno virtual**

  
   python -m venv venv
   source venv/bin/activate   # Linux / Mac
   venv\Scripts\activate      # Windows
 

3. **Instalar dependencias**

 
   pip install -r requirements.txt


---

## ▶️ Uso

Levantar el servidor:


python main.py


Por defecto se inicia en [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## 📂 Estructura del proyecto


proyecto/
 ├── perfiles/             # Perfiles JSON con regex por tipo de documento
 │    └── factura.json
 ├── extractor.py          # Motor de extracción (usa PyPDF2)
 ├── api.py                # API FastAPI que usa el extractor
 ├── main.py               # Punto de entrada (levanta uvicorn)
 ├── requirements.txt      # Dependencias
 └── README.md             # Este archivo


---

## 📑 Endpoints

### `POST /procesar_factura/`

Extrae datos de un PDF según el perfil elegido.

**Parámetros:**

* `file`: archivo PDF (obligatorio).
* `profile`: nombre del perfil (opcional, por defecto usa `factura`).

**Ejemplo con `curl`:**

curl -X POST "http://127.0.0.1:8000/procesar_factura/?profile=factura" \
  -F "file=@factura.pdf"


**Respuesta:**


{
  "perfil_usado": "factura",
  "resultado": {
    "Fecha": "15/09/2025",
    "CUIT": "20-12345678-9",
    "Total": "12345.67",
    "Fecha_Contable": "16/09/2025"
  }
}


---

## 🧩 Perfiles

Los **perfiles** definen los patrones de extracción usando expresiones regulares.
Ejemplo: `perfiles/factura.json`


{
  "name": "factura",
  "patrones": {
    "Fecha": "(?i)(?:Fecha(?:\\s+de)?(?:\\s+Emisi[oó]n)?|Emitida\\s+el)[:\\s]+(\\d{2}[-\\/\\.]\\d{2}[-\\/\\.]\\d{4})",
    "CUIT": "(?i)(?:CUIT|RUC|NIF|RFC)[:\\s]*([\\d\\-]+)",
    "Total": "(?i)(?:TOTAL(?:\\s+A\\s+PAGAR)?|Importe\\s+Total|Monto\\s+Total)[:\\s]*\\$?\\s*([\\d\\.,]+)",
    "CAE": "(?i)(?:CAE|C[oó]digo\\s+Autorizaci[oó]n)[:\\s]*([\\d]+)"
  }
}


---

## 🧪 Tests rápidos

Podés probar el extractor sin pasar por la API:


from extractor import PDFExtractor

extractor = PDFExtractor()
perfil = extractor.cargar_perfil("factura")
resultado = extractor.procesar("factura.pdf", perfil["patrones"])
print(resultado)


---

## 📜 Licencia

MIT License

