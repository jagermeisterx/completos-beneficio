import os
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

from .database import (
    init_db,
    get_inventario,
    get_inventario_publico,
    crear_donacion,
    get_donaciones,
    get_resumen_por_persona,
    get_total_dinero,
    ADMIN_TOKEN,
    cerrar_evento,
)
from .models import DonacionRequest
from .excel_export import generar_excel

app = FastAPI(title="Completada a Beneficio", docs_url=None, redoc_url=None)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.on_event("startup")
def startup():
    init_db()


def verificar_admin(token: str | None):
    if not token or token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Acceso denegado")


# --- PÁGINAS ---

@app.get("/", response_class=HTMLResponse)
def pagina_principal(request: Request):
    inventario = get_inventario_publico()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "inventario": inventario},
    )


@app.get("/admin", response_class=HTMLResponse)
def pagina_admin(request: Request, token: str | None = Query(None)):
    try:
        verificar_admin(token)
    except HTTPException:
        return templates.TemplateResponse(
            "admin.html",
            {"request": request, "autenticado": False},
        )

    inventario = get_inventario()
    donaciones = get_donaciones()
    resumen = get_resumen_por_persona()
    total_dinero = get_total_dinero()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "autenticado": True,
            "token": token,
            "inventario": inventario,
            "donaciones": donaciones,
            "resumen": resumen,
            "total_dinero": total_dinero,
        },
    )


# --- API PÚBLICA ---

@app.get("/api/inventario")
def api_inventario():
    return jsonable_encoder(get_inventario_publico())


@app.post("/api/donar")
def api_donar(data: DonacionRequest):
    resultado = crear_donacion(
        nombre=data.nombre,
        apellido=data.apellido,
        producto_id=data.producto_id,
        cantidad=data.cantidad,
    )
    if "error" in resultado:
        return JSONResponse(status_code=400, content=resultado)
    return resultado


# --- API ADMIN ---

@app.get("/api/admin/donaciones")
def api_admin_donaciones(token: str | None = Query(None)):
    verificar_admin(token)
    return jsonable_encoder(get_donaciones())


@app.get("/api/admin/resumen")
def api_admin_resumen(token: str | None = Query(None)):
    verificar_admin(token)
    resumen = get_resumen_por_persona()
    total_dinero = get_total_dinero()
    return jsonable_encoder({"resumen": resumen, "total_dinero": total_dinero})


@app.get("/api/admin/excel")
def api_admin_excel(token: str | None = Query(None)):
    verificar_admin(token)
    excel_data = generar_excel()
    return Response(
        content=excel_data.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=completada_beneficio.xlsx"
        },
    )


@app.post("/api/admin/cerrar")
def api_admin_cerrar(token: str | None = Query(None)):
    verificar_admin(token)
    resultado = cerrar_evento()
    if "error" in resultado:
        return JSONResponse(status_code=400, content=resultado)
    return resultado
