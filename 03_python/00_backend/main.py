import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from .routes import kafka_route, cassandra_route, mlflow_route, redis_route
import common.constants as constants

# LOAD THE GLOBAL CONFIG FOR SETTINGS & INITIALIZE COMPONENTS
global_config: dict = constants.global_config()
app = FastAPI()

# ADD CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ADD CUSTOM ROUTES
app.include_router(kafka_route.router)
app.include_router(cassandra_route.router)
app.include_router(mlflow_route.router)
app.include_router(redis_route.router)

# MAKE API ROOT REDIRECT TO AUTO-DOCS ENDPOINT
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# LAUNCH SERVER
if __name__ == "__main__":
    uvicorn.run(
        "00_backend.main:app", 
        host="0.0.0.0",
        port=global_config.endpoints.ports.backend_api, 
        log_level="info", 
        reload=True,
        # workers=NUM
    )