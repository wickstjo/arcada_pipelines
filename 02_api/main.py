import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.models import router as users_router
from routers.actions import router as actions_router

# INITIALIZE COMPONENTS
app = FastAPI()
API_PORT = 3003

# CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CUSTOM ROUTES
app.include_router(users_router)
app.include_router(actions_router)

# LAUNCH SERVER
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",
        port=API_PORT, 
        log_level="info", 
        reload=True,
        # workers=NUM
    )