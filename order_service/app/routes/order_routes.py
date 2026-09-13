from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.order_model import Order
from app.schemas.order_schema import OrderCreate, OrderOut, OrderUpdate


router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.id.asc()).all()
    return orders


@router.get("/user/{user_id}", response_model=List[OrderOut])
def list_orders_by_user(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.id.asc()).all()
    return orders


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    order = Order(
        user_id=payload.user_id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        total_price=payload.total_price,
        status=payload.status,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: int, payload: OrderUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if payload.user_id is not None:
        order.user_id = payload.user_id

    if payload.product_id is not None:
        order.product_id = payload.product_id

    if payload.quantity is not None:
        order.quantity = payload.quantity

    if payload.total_price is not None:
        order.total_price = payload.total_price

    if payload.status is not None:
        order.status = payload.status

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    db.delete(order)
    db.commit()
    return None
