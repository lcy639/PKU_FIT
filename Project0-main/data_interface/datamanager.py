
import sqlite3
import json
import logging
import os


from contextlib import contextmanager
from typing import Optional, Dict, Any, Iterator, Tuple, List
from passlib.hash import pbkdf2_sha256
from dataclasses import dataclass, asdict


from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import json

@dataclass
class TrainingInfo:
    timestamp: str
    exercises: List[str]  # 每个动作是一个字典
    n_group: List[int]                      # 总组数，整数

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainingInfo":
        return cls(
            timestamp=data['timestamp'],
            exercises=data["exercises"],
            n_group=data["n_group"]
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "TrainingInfo":
        return cls.from_dict(json.loads(json_str))


@dataclass
class BodyStats:
    timestamp: str
    height: float
    weight: float
    body_fat: float = None
    bmr: float = None

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典格式"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainingInfo":
        """从字典反序列化"""
        return cls(
            time=data["time"],
            height=data["height"],
            weight=data["weight"]
        )

    def to_json(self) -> str:
        """序列化为JSON字符串"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "TrainingInfo":
        """从JSON字符串反序列化"""
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BodyStats":
        """从字典反序列化"""
        return cls(
            timestamp=data["timestamp"],  # 注意字段名
            height=data["height"],
            weight=data["weight"],
            
        )

    def to_json(self) -> str:
        """序列化为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "BodyStats":
        """从 JSON 字符串反序列化"""
        return cls.from_dict(json.loads(json_str))


class LiteDataManager:
    def __init__(self, db_path: str = ':memory:') -> None:
        self.db_path: str = db_path
        self.current_user: Optional[Dict[str, Any]] = None
        self.logger: logging.Logger = logging.getLogger(
            self.__class__.__name__)

        # 初始化数据库
        self._init_db()
        self.logger.info(
            "Initialized LiteDataManager with database: %s", db_path
        )

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
            # 用户表
            cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password_hash TEXT
                )
                '''
            )

            # 训练数据表（支持多记录）
            cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    exercises TEXT NOT NULL,
                    n_group TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    UNIQUE(user_id, timestamp)
                )
                '''
            )

            # 身体数据表（支持多记录）
            cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS body_stats (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    height REAL NOT NULL,
                    weight REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    UNIQUE(user_id, timestamp)
                )'''
            )

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
            self.logger.warning(
                "Registration failed - username exists: %s", username)
            raise ValueError("用户名已存在") from e

    def save_training_record(self, record: TrainingInfo) -> int:
        """保存训练记录：若已存在，则合并并更新"""
        if not self.current_user:
            raise PermissionError("请先登录")

        try:
            with self._get_cursor() as cur:
                user_id = self.current_user['id']
                timestamp = record.timestamp

                # 查找是否已有记录
                cur.execute(
                    '''
                    SELECT exercises, n_group
                    FROM training_data
                    WHERE user_id = ? AND timestamp = ?
                    ''',
                    (
                        user_id,
                        json.dumps(timestamp)
                    )
                )
                existing = cur.fetchone()

                if existing:
                    old_exercises = json.loads(existing[0])
                    old_n_group = json.loads(existing[1])

                    temp = dict()
                    for exercise, n_group in zip(old_exercises, old_n_group):
                        temp[exercise] = int(n_group)  # 确保是整数
                    for exercise, n_group in zip(record.exercises, record.n_group):
                        if exercise in temp:
                            temp[exercise] += int(n_group)  # 累加整数
                        else:
                            temp[exercise] = int(n_group)   # 新动作直接赋值

                    updated_exercises = list(temp.keys())
                    updated_n_group = list(temp.values())

                    cur.execute(
                        '''
                        UPDATE training_data
                        SET exercises = ?, n_group = ?
                        WHERE user_id = ? AND timestamp = ?
                        ''',
                        (
                            json.dumps(updated_exercises),
                            json.dumps(updated_n_group),
                            user_id,
                            json.dumps(timestamp)
                        )
                    )

                    self.logger.info("Updated existing training record")
                    return 0  # 可返回 0 或其他标识更新成功

                else:
                    # 新记录插入
                    cur.execute(
                        '''
                        INSERT INTO training_data
                            (user_id, timestamp, exercises, n_group)
                        VALUES (?, ?, ?, ?)
                        ''',
                        (
                            user_id,
                            json.dumps(timestamp),
                            json.dumps(record.exercises),
                            json.dumps(record.n_group)
                        )
                    )
                    record_id = cur.lastrowid
                    self.logger.info(
                        "Inserted new training record ID: %d", record_id)
                    return record_id

        except Exception as e:
            self.logger.error("Failed to save training record: %s", str(e))
            raise

    def get_training_records(self, limit: int = 10) -> List[TrainingInfo]:
        """获取最近训练记录"""
        if not self.current_user:
            raise PermissionError("请先登录")

        try:
            with self._get_cursor() as cur:
                cur.execute(
                    '''
                    SELECT timestamp, exercises, n_group
                    FROM training_data
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    ''',
                    (
                        self.current_user['id'],
                        limit
                    )
                )

                return [
                    TrainingInfo(
                        timestamp=json.loads(row[0]),
                        exercises=json.loads(row[1]),
                        n_group=json.loads(row[2])
                    ) for row in cur.fetchall()
                ]
        except Exception as e:
            self.logger.error("Failed to get training records: %s", str(e))
            raise

    # 新增身体数据操作方法
    def save_body_stats(self, stats: BodyStats) -> int:
        """保存身体数据"""
        if not self.current_user:
            raise PermissionError("请先登录")

        try:
            with self._get_cursor() as cur:
                cur.execute(
                    '''
                    INSERT INTO body_stats
                        (user_id, timestamp, height, weight)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id, timestamp) DO UPDATE SET
                        height = excluded.height,
                        weight = excluded.weight
                    ''',
                    (
                        self.current_user['id'],
                        stats.timestamp,
                        stats.height,
                        stats.weight
                    )
                )
                record_id = cur.lastrowid
                self.logger.info("Saved body stats ID: %d", record_id)
                return record_id
        except Exception as e:
            self.logger.error("Failed to save body stats: %s", str(e))
            raise

    def get_body_stats_history(self, limit: int = 10) -> List[BodyStats]:
        """获取身体数据历史"""
        if not self.current_user:
            raise PermissionError("请先登录")

        try:
            with self._get_cursor() as cur:
                cur.execute(
                    '''
                    SELECT timestamp, height, weight
                    FROM body_stats
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    ''',
                    (
                        self.current_user['id'],
                        limit
                    )
                )

                return [
                    BodyStats(
                        timestamp=row[0],
                        height=row[1],
                        weight=row[2]
                    ) for row in cur.fetchall()
                ]
        except Exception as e:
            self.logger.error("Failed to get body stats: %s", str(e))
            raise
    
    
    def logout(self) -> None:
        """登出"""
        if self.current_user:
            self.logger.info(
                "User logging out: %s", self.current_user['username']
            )
            self.current_user = None
        else:
            self.logger.warning("Logout attempted with no active session")

    def get_latest_body_stats(self) -> Optional[BodyStats]:
        if not self.current_user:
            raise PermissionError("请先登录")

        with self._get_cursor() as cur:
            cur.execute(
                '''
                SELECT timestamp, height, weight, body_fat, bmr
                FROM body_stats
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
                ''',
                (self.current_user['id'],)
            )
            row = cur.fetchone()
            if row:
                return BodyStats(
                    timestamp=row[0],
                    height=row[1],
                    weight=row[2],
                    body_fat=row[3],
                    basal_metabolic_rate=row[4]
                )
        return None

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
    manager = LiteDataManager('./data/test2.db')
    try:
        manager.register('raymond', 'password')
    except ValueError:
        print('already registered')
    manager.login('raymond', 'password')
    manager.save_training_record(
        TrainingInfo(
            '20250522',
            ['push_up', 'dead_lift'],
            [15, 15]
        )
    )
    manager.save_training_record(
        TrainingInfo(
            '20250521',
            ['push_up', 'dead_lift'],
            [15, 15]
        )
    )
    print(manager.get_training_records())
    manager.logout()
