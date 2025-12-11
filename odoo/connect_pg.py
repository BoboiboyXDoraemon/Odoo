import xmlrpc.client
import psycopg2
from psycopg2 import sql
import sys

# === THÔNG SỐ ODOO ===
ODOO_URL = "http://localhost:8069"
DB_NAME = "demo"
USERNAME = "admin"
PASSWORD = "admin"

# === THÔNG SỐ PostgreSQL ===
DB_USER = "bxd"
DB_PASSWORD = "konodioda"
DB_HOST = "localhost"
DB_PORT = "5432"

# === 1. Kết nối PostgreSQL để đọc dữ liệu ===
try:
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()
    print("✅ Kết nối PostgreSQL thành công!")

    # Kiểm tra bảng res_partner
    cur.execute("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname='public' AND tablename='res_partner';
    """)
    if cur.fetchone():
        print("ℹ️ Bảng 'res_partner' tồn tại trong DB.")

        # Lấy tất cả contact hiện có
        cur.execute("""
            SELECT id, name, email, phone, company_id
            FROM res_partner
            ORDER BY id DESC
            LIMIT 5;
        """)
        rows = cur.fetchall()
        print("📄 Một số contact hiện có trong DB:")
        for row in rows:
            print(row)
    else:
        print("⚠️ Bảng 'res_partner' chưa tồn tại trong DB.")

    cur.close()
    conn.close()

except Exception as e:
    print("❌ Lỗi kết nối hoặc truy xuất PostgreSQL:", e)
    sys.exit(1)

# === 2. Kết nối tới Odoo ===
try:
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(DB_NAME, USERNAME, PASSWORD, {})
    if not uid:
        raise Exception("❌ Đăng nhập thất bại vào Odoo")
    print(f"✅ Đăng nhập Odoo thành công! UID = {uid}")
except Exception as e:
    print("❌ Lỗi đăng nhập Odoo:", e)
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

# === 3. Dữ liệu contact mới ===
new_contact = {
    'name': 'Nguyen Van B',
    'email': 'nguyen@gmail.com',
    'phone': '0123456789',
    'company_id': 1,
    'customer_rank': 1,
    'supplier_rank': 0,
    'type': 'contact'
}

# === 4. Thêm contact vào Odoo ===
try:
    contact_id = models.execute_kw(
        DB_NAME, uid, PASSWORD,
        'res.partner', 'create',
        [new_contact]
    )
    print(f"✅ Contact đã tạo thành công trên Odoo với ID: {contact_id}")
except Exception as e:
    print("❌ Lỗi tạo contact trên Odoo:", e)
    sys.exit(1)

# === 5. Truy xuất record vừa tạo từ Odoo ===
try:
    record = models.execute_kw(
        DB_NAME, uid, PASSWORD,
        'res.partner', 'read',
        [[contact_id]],
        {'fields': ['id', 'name', 'email', 'phone', 'company_id']}
    )
    print("Thông tin contact vừa tạo trên Odoo:", record)
except Exception as e:
    print("❌ Lỗi đọc contact vừa tạo:", e)
