from typing import Optional, Dict
from fastapi import HTTPException
from generated.models.order import Order
from db import db_pool

class StoreService:
    @staticmethod
    def place_order(order: Order) -> Order:
        with db_pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (id, petId, quantity, shipDate, status, complete)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (order.id, order.petId, order.quantity, order.shipDate, order.status, order.complete))
            conn.commit()
        return order

    @staticmethod
    def get_order(orderId: int) -> Order:
        with db_pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM orders WHERE id = ?', (orderId,))
            order_row = cursor.fetchone()
            if not order_row:
                raise HTTPException(status_code=404, detail="Order not found")
            order_id, petId, quantity, shipDate, status, complete = order_row
            return Order(
                id=order_id,
                petId=petId,
                quantity=quantity,
                shipDate=shipDate,
                status=status,
                complete=complete
            )

    @staticmethod
    def delete_order(orderId: int) -> dict:
        with db_pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM orders WHERE id = ?', (orderId,))
            order_row = cursor.fetchone()
            if not order_row:
                raise HTTPException(status_code=404, detail="Order not found")
            cursor.execute('DELETE FROM orders WHERE id = ?', (orderId,))
            conn.commit()
        return {"message": "Order deleted"}

    @staticmethod
    def get_inventory() -> Dict[str, int]:
        with db_pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT status, COUNT(*) FROM pets GROUP BY status')
            inventory_rows = cursor.fetchall()
            inventory = {}
            for status, count in inventory_rows:
                inventory[status] = count
        return inventory