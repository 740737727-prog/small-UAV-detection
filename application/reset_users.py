import sqlite3
import os

def reset_users():
    """清空用户表，保留数据库结构"""
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'drone_monitor.db')
    
    if not os.path.exists(db_path):
        print("Database file does not exist, no reset needed")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 清空用户表
        cursor.execute('DELETE FROM users')
        
        # 重置自增ID
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
        
        conn.commit()
        print("User information successfully cleared!")
        print("System restored to initial state, ready for new admin account registration.")
        
    except Exception as e:
        print(f"Reset failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reset_users()
