from fastapi import FastAPI


app = FastAPI()

@app.get("/healthCheck")
async def root():
    return {"message": "Hello World"}