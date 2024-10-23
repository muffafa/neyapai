from fastapi import FastAPI
from server.routers import user
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NeYapAI API")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router)

@app.get("/")
async def root():
    return {"message": "AI Suppported Learning API"}
