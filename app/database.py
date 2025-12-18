"""
Database va ma'lumotlar boshqarish
SQLite bilan ishlash
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import json
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path("data/bot.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class Database:
    """Database boshqaruvchi"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Database ulanishi"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Jadvallarni yaratish"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_admin BOOLEAN DEFAULT 0,
                is_banned BOOLEAN DEFAULT 0,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                downloads_count INTEGER DEFAULT 0,
                storage_used INTEGER DEFAULT 0
            )
        ''')

        # Download history jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                format TEXT NOT NULL,
                title TEXT,
                file_size INTEGER,
                status TEXT,
                download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completion_time TIMESTAMP,
                error_message TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Messages jadvali (broadcast uchun)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                is_broadcast BOOLEAN DEFAULT 0,
                target_users TEXT,
                sent_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(user_id)
            )
        ''')

        # Statistics jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                total_users INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0,
                total_downloads INTEGER DEFAULT 0,
                successful_downloads INTEGER DEFAULT 0,
                failed_downloads INTEGER DEFAULT 0,
                total_storage_used INTEGER DEFAULT 0,
                avg_download_time REAL DEFAULT 0,
                platforms_used TEXT
            )
        ''')

        # Admin logs jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                target_user_id INTEGER,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users(user_id),
                FOREIGN KEY (target_user_id) REFERENCES users(user_id)
            )
        ''')

        # Notifications jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("✅ Database jadvallari yaratildi")

    # USER OPERATSIYALARI

    def add_user(self, user_id: int, username: str = "", first_name: str = "",
                 last_name: str = "", is_admin: bool = False) -> bool:
        """Foydalanuvchi qo'shish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users 
                (user_id, username, first_name, last_name, is_admin)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, is_admin))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"User qo'shishda xatolik: {e}")
            return False

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Foydalanuvchi ma'lumoti"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            conn.close()
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"User olishda xatolik: {e}")
            return None

    def get_all_users(self, is_admin: Optional[bool] = None,
                     is_banned: Optional[bool] = None) -> List[Dict]:
        """Barcha foydalanuvchilar"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = 'SELECT * FROM users'
            params = []

            if is_admin is not None:
                query += ' WHERE is_admin = ?'
                params.append(is_admin)

            if is_banned is not None:
                if params:
                    query += ' AND is_banned = ?'
                else:
                    query += ' WHERE is_banned = ?'
                params.append(is_banned)

            cursor.execute(query, params)
            users = cursor.fetchall()
            conn.close()
            return [dict(user) for user in users]
        except Exception as e:
            logger.error(f"Foydalanuvchilar olishda xatolik: {e}")
            return []

    def ban_user(self, user_id: int, reason: str = "") -> bool:
        """Foydalanuvchini ban qilish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            logger.info(f"👤 {user_id} ban qilindi. Sabab: {reason}")
            return True
        except Exception as e:
            logger.error(f"Ban qilishda xatolik: {e}")
            return False

    def unban_user(self, user_id: int) -> bool:
        """Ban olib tashlash"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            logger.info(f"👤 {user_id} unbanned")
            return True
        except Exception as e:
            logger.error(f"Unban qilishda xatolik: {e}")
            return False

    def make_admin(self, user_id: int) -> bool:
        """Admin qilish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_admin = 1 WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            logger.info(f"👑 {user_id} admin qilindi")
            return True
        except Exception as e:
            logger.error(f"Admin qilishda xatolik: {e}")
            return False

    def remove_admin(self, user_id: int) -> bool:
        """Admin o'chirish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_admin = 0 WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            logger.info(f"👑 {user_id} adminlik olib tashlandi")
            return True
        except Exception as e:
            logger.error(f"Admin o'chirish xatosi: {e}")
            return False

    def update_user_activity(self, user_id: int):
        """Foydalanuvchi faoliyatini yangilash"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = ?',
                (user_id,)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Faoliyat yangilashda xatolik: {e}")

    # DOWNLOAD OPERATSIYALARI

    def log_download(self, user_id: int, url: str, format_type: str,
                    title: str = "", file_size: int = 0, status: str = "pending") -> int:
        """Download logga qo'shish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO downloads (user_id, url, format, title, file_size, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, url, format_type, title, file_size, status))
            conn.commit()
            download_id = cursor.lastrowid
            conn.close()
            return download_id
        except Exception as e:
            logger.error(f"Download log qo'shishda xatolik: {e}")
            return 0

    def complete_download(self, download_id: int, file_size: int = 0):
        """Download tugallash"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE downloads 
                SET status = 'completed', 
                    completion_time = CURRENT_TIMESTAMP,
                    file_size = ?
                WHERE id = ?
            ''', (file_size, download_id))

            # User statistikasini yangilash
            cursor.execute('SELECT user_id FROM downloads WHERE id = ?', (download_id,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
                cursor.execute('''
                    UPDATE users 
                    SET downloads_count = downloads_count + 1,
                        storage_used = storage_used + ?
                    WHERE user_id = ?
                ''', (file_size, user_id))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Download tugallashda xatolik: {e}")

    def fail_download(self, download_id: int, error_message: str = ""):
        """Download muvaffaqiyatsiz"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE downloads 
                SET status = 'failed', 
                    completion_time = CURRENT_TIMESTAMP,
                    error_message = ?
                WHERE id = ?
            ''', (error_message, download_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Download failure qo'shishda xatolik: {e}")

    def get_user_downloads(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Foydalanuvchining yuklab olishlari"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM downloads 
                WHERE user_id = ? 
                ORDER BY download_time DESC 
                LIMIT ?
            ''', (user_id, limit))
            downloads = cursor.fetchall()
            conn.close()
            return [dict(d) for d in downloads]
        except Exception as e:
            logger.error(f"Yuklab olishlari o'qishda xatolik: {e}")
            return []

    # MESSAGE OPERATSIYALARI

    def send_message(self, sender_id: int, message_text: str,
                    target_users: Optional[List[int]] = None,
                    is_broadcast: bool = False) -> int:
        """Xabar yuborish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            targets_json = json.dumps(target_users) if target_users else None

            cursor.execute('''
                INSERT INTO messages (sender_id, message_text, target_users, is_broadcast)
                VALUES (?, ?, ?, ?)
            ''', (sender_id, message_text, targets_json, is_broadcast))

            conn.commit()
            message_id = cursor.lastrowid
            conn.close()
            return message_id
        except Exception as e:
            logger.error(f"Xabar yuborish xatosi: {e}")
            return 0

    def get_pending_messages(self, limit: int = 10) -> List[Dict]:
        """Yuborilmagan xabarlar"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM messages 
                WHERE sent_count = 0
                ORDER BY created_at
                LIMIT ?
            ''', (limit,))
            messages = cursor.fetchall()
            conn.close()
            return [dict(m) for m in messages]
        except Exception as e:
            logger.error(f"Xabarlarni o'qishda xatolik: {e}")
            return []

    def update_message_status(self, message_id: int, sent_count: int, failed_count: int):
        """Xabar statusini yangilash"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE messages 
                SET sent_count = ?, failed_count = ?
                WHERE id = ?
            ''', (sent_count, failed_count, message_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Xabar statusini yangilashda xatolik: {e}")

    # NOTIFICATION OPERATSIYALARI

    def add_notification(self, user_id: int, message: str,
                        notification_type: str = "info") -> int:
        """Bildirishnoma qo'shish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notifications (user_id, message, notification_type)
                VALUES (?, ?, ?)
            ''', (user_id, message, notification_type))
            conn.commit()
            notif_id = cursor.lastrowid
            conn.close()
            return notif_id
        except Exception as e:
            logger.error(f"Bildirishnoma qo'shishda xatolik: {e}")
            return 0

    def get_unread_notifications(self, user_id: int) -> List[Dict]:
        """O'qilmagan bildirishnomalar"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM notifications 
                WHERE user_id = ? AND is_read = 0
                ORDER BY created_at DESC
            ''', (user_id,))
            notifs = cursor.fetchall()
            conn.close()
            return [dict(n) for n in notifs]
        except Exception as e:
            logger.error(f"Bildirishnomalarni o'qishda xatolik: {e}")
            return []

    def mark_notification_read(self, notification_id: int):
        """Bildirishnomani o'qish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notifications 
                SET is_read = 1, read_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (notification_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Bildirishnoma o'qish xatosi: {e}")

    # ADMIN LOG OPERATSIYALARI

    def log_admin_action(self, admin_id: int, action: str,
                        target_user_id: Optional[int] = None, details: str = ""):
        """Admin amalni logga qo'shish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO admin_logs (admin_id, action, target_user_id, details)
                VALUES (?, ?, ?, ?)
            ''', (admin_id, action, target_user_id, details))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Admin log qo'shishda xatolik: {e}")

    def get_admin_logs(self, limit: int = 50) -> List[Dict]:
        """Admin loggari"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM admin_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            logs = cursor.fetchall()
            conn.close()
            return [dict(log) for log in logs]
        except Exception as e:
            logger.error(f"Admin loggani o'qishda xatolik: {e}")
            return []

    # STATISTICS

    def get_statistics(self) -> Dict:
        """Bot statistikasi"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_banned = 0')
            total_users = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) as count FROM users WHERE last_activity > datetime("now", "-1 day")')
            active_users = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) as count FROM downloads WHERE status = "completed"')
            successful_downloads = cursor.fetchone()['count']

            cursor.execute('SELECT COUNT(*) as count FROM downloads WHERE status = "failed"')
            failed_downloads = cursor.fetchone()['count']

            cursor.execute('SELECT SUM(storage_used) as total FROM users')
            result = cursor.fetchone()
            total_storage = result['total'] or 0

            cursor.execute('SELECT AVG(CAST((julianday(completion_time) - julianday(download_time)) * 86400 AS INTEGER)) as avg_time FROM downloads WHERE status = "completed"')
            result = cursor.fetchone()
            avg_time = result['avg_time'] or 0

            conn.close()

            return {
                'total_users': total_users,
                'active_users': active_users,
                'successful_downloads': successful_downloads,
                'failed_downloads': failed_downloads,
                'total_storage_used': total_storage,
                'avg_download_time': avg_time,
            }
        except Exception as e:
            logger.error(f"Statistika olishda xatolik: {e}")
            return {}


# Global database instance
db = Database()

