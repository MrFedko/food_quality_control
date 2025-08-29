import sqlite3


class Database:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row

    def execute(self, query: str, params: tuple = (), fetchone=False, fetchall=False):
        with self.connection:
            cursor = self.connection.execute(query, params)
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()

    def create_table_users(self):
        self.execute("""CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    surname TEXT NOT NULL,
    user_tg_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    phone_number TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")

    def create_table_reviews(self):
        self.execute("""CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worksheet_id TEXT NOT NULL,
    rev_date TIMESTAMP DEFAULT (datetime('now','+3 hours')),
    status TEXT NOT NULL,
    dish_name TEXT NOT NULL,
    photo_path TEXT,
    description TEXT NOT NULL,
    price TEXT,
    surname_reviewer TEXT NOT NULL,
    surname_chef TEXT NOT NULL,
    final_status TEXT NOT NULL,
    ref_id TEXT
);""")

    def new_user(self, username, surname, user_tg_id, role, phone_number):
        self.execute(
            "INSERT INTO users (username, surname, user_tg_id, role, phone_number) VALUES (?, ?, ?, ?, ?)",
            (username, surname, user_tg_id, role, phone_number))

    def read_user(self, user_tg_id):
        return self.execute("SELECT * FROM users WHERE user_tg_id = ?", (user_tg_id,), fetchone=True)

    def read_restaurant(self, restaurant_id):
        return self.execute("SELECT * FROM reviews WHERE worksheet_id = ?", (restaurant_id,), fetchone=True)

    def new_review(self, worksheet_id, status, dish_name, photo_path, description, price, surname_reviewer, surname_chef, final_status, ref_id):
        self.execute(
            "INSERT INTO reviews (worksheet_id, status, dish_name, photo_path, description, price, surname_reviewer, surname_chef, final_status, ref_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (worksheet_id, status, dish_name, photo_path, description, price, surname_reviewer, surname_chef, final_status, ref_id))

    def count_check_reviews(self, restaurant_id):
        result = self.execute("SELECT COUNT(*) as count FROM reviews WHERE worksheet_id = ? AND final_status = 'На доработку' AND ref_id = 0", (restaurant_id,), fetchone=True)
        return result["count"] if result else 0

    def get_reviews_for_check(self, restaurant_id):
        return self.execute("SELECT * FROM reviews WHERE worksheet_id = ? AND final_status = 'На доработку' AND ref_id = 0", (restaurant_id,), fetchall=True)

    def get_dish_info(self, ref_id):
        result = self.execute("SELECT dish_name, description FROM reviews WHERE id = ?", (ref_id,), fetchone=True)
        return result["dish_name"], result["description"] if result else (None, None)

    def update_ref_id(self, review_id, ref_id):
        self.execute("UPDATE reviews SET ref_id = ? WHERE id = ?", (ref_id, review_id))
