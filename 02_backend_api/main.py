import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import kafka_route, cassandra_route, redis_route, config_route
import funcs.misc as misc

# LOAD THE GLOBAL CONFIG FOR SETTINGS & INITIALIZE COMPONENTS
global_config = misc.load_global_config()
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
app.include_router(redis_route.router)
app.include_router(config_route.router)

# LIST OUT ENDPOINTS AT ROOT
@app.get('/')
async def read_root():
    return {
        'endpoints': [
            '/docs',
            '/kafka',
            '/cassandra',
            '/redis',
            '/config',
        ]
    }

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