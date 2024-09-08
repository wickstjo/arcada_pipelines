import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import kafka, cassandra
from utils.misc import load_global_config

# LOAD THE GLOBAL CONFIG FOR SETTINGS & INITIALIZE COMPONENTS
global_config = load_global_config()
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
app.include_router(kafka.router)
app.include_router(cassandra.router)

# LAUNCH SERVER
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",
        port=global_config.backend.api_port, 
        log_level="info", 
        reload=True,
        # workers=NUM
    )