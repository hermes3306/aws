from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, create_tables
from redis_client import get_redis
from models import User, Product, Order, OrderItem
from auth import get_current_user, create_access_token, get_password_hash, authenticate_user
from pydantic import BaseModel
from typing import List
import redis
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from auth import authenticate_user, create_access_token

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create database tables
create_tables()

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str




class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    inventory: int

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    inventory: int

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: float
    items: List[dict]

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email, password_hash=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"Received login attempt for username: {form_data.username}")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db), redis: redis.Redis = Depends(get_redis), current_user: User = Depends(get_current_user)):
    db_order = Order(user_id=current_user.id, status="pending", total_amount=0)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    total_amount = 0
    order_items = []

    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or product.inventory < item.quantity:
            db.delete(db_order)
            db.commit()
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} is not available in the requested quantity")

        order_item = OrderItem(order_id=db_order.id, product_id=item.product_id, quantity=item.quantity, price=product.price)
        db.add(order_item)
        total_amount += product.price * item.quantity
        order_items.append({"product_id": item.product_id, "quantity": item.quantity, "price": product.price})

        # Update product inventory
        product.inventory -= item.quantity
        db.add(product)

        # Update Redis cache
        redis.set(f"product:{product.id}:inventory", product.inventory)

    db_order.total_amount = total_amount
    db_order.status = "completed"
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Cache order status in Redis
    redis.set(f"order:{db_order.id}:status", db_order.status)

    return {"id": db_order.id, "user_id": db_order.user_id, "status": db_order.status, "total_amount": db_order.total_amount, "items": order_items}


@app.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = db.query(User).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/orders", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return [{"id": order.id, "user_id": order.user_id, "status": order.status, "total_amount": order.total_amount, 
             "items": [{"product_id": item.product_id, "quantity": item.quantity, "price": item.price} for item in order.order_items]} 
            for order in orders]

@app.get("/orders", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).all()
    return [{"id": order.id, "user_id": order.user_id, "status": order.status, "total_amount": order.total_amount, 
             "items": [{"product_id": item.product_id, "quantity": item.quantity, "price": item.price} for item in order.order_items]} 
            for order in orders]

@app.get("/order_items", response_model=List[dict])
def get_order_items(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order_items = db.query(OrderItem).all()
    return [{"id": item.id, "order_id": item.order_id, "product_id": item.product_id, "quantity": item.quantity, "price": item.price}
            for item in order_items]

@app.get("/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    products = db.query(Product).all()
    return products

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)