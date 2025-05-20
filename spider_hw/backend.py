
import sqlite3
import json
import logging
import os


from contextlib import contextmanager
from typing import Optional, Dict, Any, Iterator, Tuple, List
from passlib.hash import pbkdf2_sha256
from dataclasses import dataclass, asdict


@dataclass
class TrainingInfo:
    exercises: List[str]
    parts: List[List[str]]
    time: List[int]

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典格式"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainingInfo":
        """从字典反序列化"""
        return cls(
            exercises=data["exercises"],
            parts=data["parts"],
            time=data["time"]
        )

    def to_json(self) -> str:
        """序列化为JSON字符串"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "TrainingInfo":
        """从JSON字符串反序列化"""
        return cls.from_dict(json.loads(json_str))


class LiteDataManager:
    def __init__(self, db_path: str = ':memory:') -> None:
        self.db_path: str = db_path
        self.current_user: Optional[Dict[str, Any]] = None
        self.logger: logging.Logger = logging.getLogger(
            self.__class__.__name__)

        # 初始化数据库
        self._init_db()
        self.logger.info("Initialized LiteDataManager with database: %s", db_path)

    @contextmanager
    def _get_cursor(self) -> Iterator[sqlite3.Cursor]:
        """自动管理数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA foreign_keys = ON')
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error("Database operation failed: %s", str(e))
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        """初始化数据库表结构"""
        with self._get_cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password_hash TEXT
                )''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS user_data (
                    user_id INTEGER PRIMARY KEY,
                    data TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')
        self.logger.debug("Database tables initialized")

    def login(self, username: str, password: str) -> bool:
        """登录实现"""
        self.logger.info("Login attempt for user: %s", username)
        try:
            with self._get_cursor() as cur:
                cur.execute(
                    'SELECT id, password_hash FROM users WHERE username=?',
                    (username,)
                )
                result: Optional[Tuple[int, str]] = cur.fetchone()

            if not result:
                self.logger.warning(
                    "Login failed - user not found: %s", username)
                raise ValueError("用户不存在")

            user_id, stored_hash = result
            if pbkdf2_sha256.verify(password, stored_hash):
                self.current_user = {'id': user_id, 'username': username}
                self.logger.info("User logged in: %s", username)
                return True
            self.logger.warning("Invalid password for user: %s", username)
            raise ValueError("密码错误")
        except Exception as e:
            self.logger.error("Login error: %s", str(e))
            raise

    def register(self, username: str, password: str) -> bool:
        """注册功能"""
        self.logger.info("Registration attempt for user: %s", username)
        try:
            with self._get_cursor() as cur:
                cur.execute(
                    'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                    (username, pbkdf2_sha256.hash(password))
                )
            self.logger.info("User registered: %s", username)
            return True
        except sqlite3.IntegrityError as e:
            self.logger.warning("Registration failed - username exists: %s", username)
            raise ValueError("用户名已存在") from e

    def get_data(self) -> Dict[str, Any]:
        """读取用户数据"""
        if not self.current_user:
            self.logger.error("Data access attempted without login")
            raise PermissionError("请先登录")
        try:
            with self._get_cursor() as cur:
                cur.execute(
                    'SELECT data FROM user_data WHERE user_id=?',
                    (self.current_user['id'],)
                )
                result: Optional[Tuple[str]] = cur.fetchone()
            data = json.loads(result[0]) if result else {}
            self.logger.debug("Data retrieved for user: %s", self.current_user['username'])
            return data
        except Exception as e:
            self.logger.error("Data retrieval failed: %s", str(e))
            raise

    def update_data(self, new_data: Dict[str, Any]) -> bool:
        """更新用户数据"""
        if not self.current_user:
            self.logger.error("Data update attempted without login")
            raise PermissionError("请先登录")
        try:
            with self._get_cursor() as cur:
                cur.execute('''
                    INSERT INTO user_data (user_id, data)
                    VALUES (?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET data=excluded.data
                    ''', (self.current_user['id'], json.dumps(new_data))
                )
            self.logger.info("Data updated for user: %s", self.current_user['username'])
            return True
        except Exception as e:
            self.logger.error("Data update failed: %s", str(e))
            raise

    def logout(self) -> None:
        """登出"""
        if self.current_user:
            self.logger.info("User logging out: %s", self.current_user['username'])
            self.current_user = None
        else:
            self.logger.warning("Logout attempted with no active session")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('db_test.log'),
            logging.StreamHandler()
        ]
    )
    os.makedirs('data', exist_ok=True)
    manager = LiteDataManager('./data/test1.db')
    try:
        manager.register('raymond', 'password')
    except ValueError:
        print('already registered')
    manager.login('raymond', 'password')
    manager.update_data({'20250502': TrainingInfo(['push_up', 'running'], [['arm', 'chest'], ['Cardiovascular']], [30, 25]).to_dict()})
    data = manager.get_data()
    print(data)
    data['20250503'] = TrainingInfo(['deadlift'], [['hip']], [40]).to_dict()
    manager.update_data(data)
    data = manager.get_data()
    print(data)
    manager.logout()