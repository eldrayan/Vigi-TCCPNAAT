"""
Descrição: Inicializa a API FastAPI e registra suas rotas HTTP.
Autor: Leôncio Ferreira
"""

from fastapi import FastAPI

from app.modules.inspections.routes import router as inspections_router

app = FastAPI(
    title="Vigi API",
    version="0.1.0",
)
app.include_router(inspections_router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
