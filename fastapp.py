from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class argu(BaseModel):
    x: int
    y: int

@app.get('/sum')
def summi(a: int, b: int) -> int:
    return a + b

@app.get('/multiply')
async def multiply(x: int, y: int):
    return x*y