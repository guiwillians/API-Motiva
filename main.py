from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Importa suas funções do arquivo de modelo
from model_pred import rodar_pipeline, ESPECIES

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Desafio Motiva")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PrevisaoRequest(BaseModel):
    lat: float
    lon: float
    data_ini: str
    data_fim: str
    especie_key: str = "bermuda"
    data_corte: Optional[str] = None
    peso_gdd: float = 0.4
    peso_rue: float = 0.6

@app.post("/api/prever")
def prever(req: PrevisaoRequest):
    if req.especie_key not in ESPECIES:
        raise HTTPException(status_code=400, detail="Espécie inválida")

    try:
        df = rodar_pipeline(
            lat=req.lat, lon=req.lon, data_ini=req.data_ini, data_fim=req.data_fim,
            especie_key=req.especie_key, data_corte=req.data_corte,
            peso_gdd=req.peso_gdd, peso_rue=req.peso_rue
        )

        df_saida = df[["altura_estimada_cm", "crescimento_diario_cm"]].fillna(0).round(2)
        df_saida.index = df_saida.index.astype(str)
        
        return {"status": "sucesso", "dados": df_saida.to_dict(orient="index")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))