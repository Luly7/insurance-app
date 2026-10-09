from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import engine, get_db
import models
from routers import profiles, vehicles, quotes, policies

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Family Insurance Manager")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(profiles.router)
app.include_router(vehicles.router)
app.include_router(quotes.router)
app.include_router(policies.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    members = db.query(models.FamilyMember).all()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"members": members}
    )
