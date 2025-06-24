from typing import List, Optional
from fastapi import HTTPException
from generated.models.user import User
from db import db_pool

class UserService:
    @staticmethod
    def create_user(user: User) -> User:
        with db_pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (id, username, firstName, lastName, email, password, phone, userStatus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user.id, user.username, user.firstName, user.lastName, user.email, user.password, user.phone, user.userStatus))
            conn.commit()
        return user

    @staticmethod
    def create_users_with_list(users: List[User]) -> List[User]:
        with db_pool.connection() as conn:
            cursor = conn.cursor()
            for user in users:
                cursor.execute('''
                    INSERT INTO users (id, username, firstName, lastName, email, password, phone, userStatus)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user.id, user.username, user.firstName, user.lastName, user.email, user.password, user.phone, user.userStatus))
            conn.commit()
        return users

    @staticmethod
    def login_user(username: Optional[str], password: Optional[str]) -> dict:
        with db_pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user_row = cursor.fetchone()
            if not user_row:
                raise HTTPException(status_code=400, detail="Invalid username/password")
        return {"token": "generated-token", "token_type": "bearer"}

    @staticmethod
    def logout_user() -> dict:
        # Implement logout logic here if needed
        return {"message": "User logged out"}

    @staticmethod
    def get_user(username: str) -> User:
        with db_pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user_row = cursor.fetchone()
            if not user_row:
                raise HTTPException(status_code=404, detail="User not found")
            user_id, user_username, firstName, lastName, email, password, phone, userStatus = user_row
            return User(
                id=user_id,
                username=user_username,
                firstName=firstName,
                lastName=lastName,
                email=email,
                password=password,
                phone=phone,
                userStatus=userStatus
            )

    @staticmethod
    def update_user(username: str, user: User) -> User:
        with db_pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users
                SET firstName = ?, lastName = ?, email = ?, password = ?, phone = ?, userStatus = ?
                WHERE username = ?
            ''', (user.firstName, user.lastName, user.email, user.password, user.phone, user.userStatus, username))
            conn.commit()
        return user

    @staticmethod
    def delete_user(username: str) -> dict:
        with db_pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user_row = cursor.fetchone()
            if not user_row:
                raise HTTPException(status_code=404, detail="User not found")
            cursor.execute('DELETE FROM users WHERE username = ?', (username,))
            conn.commit()
        return {"message": "User deleted"}