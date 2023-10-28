from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn


# Configura la conexión a la base de datos PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://databasemenu_user:ZnoY5wh7SjJ3aybp42olfAeaR6xmzWWm@dpg-ckr9rehrfc9c73djbtu0-a/databasemenu"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# Crea una instancia de la aplicación FastAPI
app = FastAPI()

# Configura el sistema de plantillas
templates = Jinja2Templates(directory="templates")

# Define el modelo de Producto
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    imagen = Column(String(255), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=False)
    precio = Column(Float, nullable=False)

# Crea la tabla en la base de datos si no existe
Base.metadata.create_all(bind=engine)

# Crea una clase Pydantic para validar la entrada de datos
class ProductCreate(BaseModel):
    imagen: str
    nombre: str
    descripcion: str
    precio: float

# Rutas para CRUD

@app.post("/products/", response_model=Product)
def create_product(product: ProductCreate):
    db = sessionmaker(bind=engine)()
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

@app.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int):
    db = sessionmaker(bind=engine)()
    product = db.query(Product).filter(Product.id == product_id).first()
    db.close()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductCreate):
    db = sessionmaker(bind=engine)()
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        db.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

@app.delete("/products/{product_id}", response_model=Product)
def delete_product(product_id: int):
    db = sessionmaker(bind=engine)()
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        db.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(product)
    db.commit()
    db.close()
    return product

# Rutas para las páginas HTML

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/create", response_class=HTMLResponse)
async def read_create(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@app.get("/read/{product_id}", response_class=HTMLResponse)
async def read_read(request: Request, product_id: int):
    product = read_product(product_id)
    return templates.TemplateResponse("read.html", {"request": request, "product": product})

@app.get("/update/{product_id}", response_class=HTMLResponse)
async def read_update(request: Request, product_id: int):
    product = read_product(product_id)
    return templates.TemplateResponse("update.html", {"request": request, "product": product})

@app.get("/delete/{product_id}", response_class=HTMLResponse)
async def read_delete(request: Request, product_id: int):
    product = read_product(product_id)
    return templates.TemplateResponse("delete.html", {"request": request, "product": product})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
