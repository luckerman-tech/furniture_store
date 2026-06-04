from django.db import connection
from decimal import Decimal

class SQLWarehouseManager:
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM Warehouses")
            return cursor.fetchall()
    
    @staticmethod
    def create(name):
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Warehouses (name) VALUES (%s) RETURNING id",
                [name]
            )
            return cursor.fetchone()[0]
    
    @staticmethod
    def update(warehouse_id, name):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE Warehouses SET name = %s WHERE id = %s",
                [name, warehouse_id]
            )
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(warehouse_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Warehouses WHERE id = %s", [warehouse_id])
            return cursor.rowcount > 0

class SQLAssortmentManager:
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT a.id, a.name, a.price, c.name as category_name, s.name as style_name
                FROM Assortment a
                JOIN Categories c ON a.category_id = c.id
                JOIN Styles s ON a.style_id = s.id
            """)
            return cursor.fetchall()
    
    @staticmethod
    def filter_by_category(category_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT a.id, a.name, a.price, c.name, s.name
                FROM Assortment a
                JOIN Categories c ON a.category_id = c.id
                JOIN Styles s ON a.style_id = s.id
                WHERE a.category_id = %s
            """, [category_id])
            return cursor.fetchall()
    
    @staticmethod
    def filter_by_price_range(min_price, max_price):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, price
                FROM Assortment
                WHERE price BETWEEN %s AND %s
            """, [min_price, max_price])
            return cursor.fetchall()

    @staticmethod
    def filter_combined(name=None, category_id=None, style_id=None, min_price=None, max_price=None):
        with connection.cursor() as cursor:
            sql = """
                SELECT a.id, a.name, a.price, c.name as category_name, s.name as style_name
                FROM Assortment a
                JOIN Categories c ON a.category_id = c.id
                JOIN Styles s ON a.style_id = s.id
                WHERE 1=1
            """
            params = []
            
            if name and name != '':
                sql += " AND a.name LIKE %s COLLATE NOCASE"
                params.append(f'%{name}%')

            if category_id and category_id != '0':
                sql += " AND a.category_id = %s"
                params.append(category_id)

            if style_id and style_id != '0':
                sql += " AND a.style_id = %s"
                params.append(style_id)
            
            if min_price and min_price != '0':
                try:
                    sql += " AND a.price >= %s"
                    params.append(float(min_price))
                except ValueError:
                    pass
            
            if max_price and max_price != '999999':
                try:
                    sql += " AND a.price <= %s"
                    params.append(float(max_price))
                except ValueError:
                    pass
            
            cursor.execute(sql, params)
            items = cursor.fetchall()
            
            result = []
            for item in items:
                result.append({
                    'id': item[0],
                    'name': item[1],
                    'price': float(item[2]),
                    'category_name': item[3],
                    'style_name': item[4]
                })
            
            return result
    
    @staticmethod
    def create(name, price, category_id, style_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Assortment (name, price, category_id, style_id)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, [name, price, category_id, style_id])
            return cursor.fetchone()[0]
    
    @staticmethod
    def update(assortment_id, name=None, price=None, category_id=None, style_id=None):
        updates = []
        params = []
        if name:
            updates.append("name = %s")
            params.append(name)
        if price:
            updates.append("price = %s")
            params.append(price)
        if category_id:
            updates.append("category_id = %s")
            params.append(category_id)
        if style_id:
            updates.append("style_id = %s")
            params.append(style_id)
        
        if updates:
            params.append(assortment_id)
            with connection.cursor() as cursor:
                cursor.execute(
                    f"UPDATE Assortment SET {', '.join(updates)} WHERE id = %s",
                    params
                )
                return cursor.rowcount > 0
        return False
    
    @staticmethod
    def delete(assortment_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Assortment WHERE id = %s", [assortment_id])
            return cursor.rowcount > 0

class SQLOrderManager:
    @staticmethod
    def get_orders_with_items(order_id=None):
        with connection.cursor() as cursor:
            if order_id:
                cursor.execute("""
                    SELECT o.id, o.datetime, c.full_name,
                           oi.id, oi.quantity, a.name, k.name
                    FROM Orders o
                    JOIN Clients c ON o.client_id = c.id
                    LEFT JOIN OrderItems oi ON o.id = oi.order_id
                    LEFT JOIN Assortment a ON oi.assortment_id = a.id
                    LEFT JOIN Kits k ON oi.kit_id = k.id
                    WHERE o.id = %s
                """, [order_id])
            else:
                cursor.execute("""
                    SELECT o.id, o.datetime, c.full_name,
                           oi.id, oi.quantity, a.name, k.name
                    FROM Orders o
                    JOIN Clients c ON o.client_id = c.id
                    LEFT JOIN OrderItems oi ON o.id = oi.order_id
                    LEFT JOIN Assortment a ON oi.assortment_id = a.id
                    LEFT JOIN Kits k ON oi.kit_id = k.id
                """)
            return cursor.fetchall()
    
    @staticmethod
    def create_order(client_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Orders (client_id, datetime) VALUES (%s, NOW()) RETURNING id",
                [client_id]
            )
            return cursor.fetchone()[0]
    
    @staticmethod
    def add_order_item(order_id, quantity, assortment_id=None, kit_id=None):
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO OrderItems (order_id, assortment_id, kit_id, quantity)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, [order_id, assortment_id, kit_id, quantity])
            return cursor.fetchone()[0]

class SQLStorageReportManager:
    @staticmethod
    def get_storage_report():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT w.name as warehouse, a.name as product, s.quantity
                FROM Storage s
                JOIN Warehouses w ON s.warehouse_id = w.id
                JOIN Assortment a ON s.assortment_id = a.id
                WHERE s.quantity > 0
                ORDER BY w.name, a.name
            """)
            return cursor.fetchall()
    
    @staticmethod
    def get_product_movement(product_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 'Приход' as type, p.datetime, p.quantity, w.name
                FROM Parishes p
                JOIN Warehouses w ON p.warehouse_id = w.id
                WHERE p.assortment_id = %s
                UNION ALL
                SELECT 'Расход' as type, e.datetime, e.quantity, w.name
                FROM Expenses e
                JOIN Warehouses w ON e.warehouse_id = w.id
                WHERE e.assortment_id = %s
                ORDER BY datetime
            """, [product_id, product_id])
            return cursor.fetchall()

class SQLParishManager:
    @staticmethod
    def create(warehouse_id, assortment_id, quantity):
        from datetime import datetime
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Parishes (warehouse_id, assortment_id, quantity, datetime)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, [warehouse_id, assortment_id, quantity, datetime.now()])
            
            parish_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO Storage (warehouse_id, assortment_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (warehouse_id, assortment_id) 
                DO UPDATE SET quantity = Storage.quantity + %s
            """, [warehouse_id, assortment_id, quantity, quantity])
            
            return parish_id

class SQLCategoryManager:
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM Categories ORDER BY id")
            return cursor.fetchall()
    
    @staticmethod
    def get_by_id(category_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM Categories WHERE id = %s", [category_id])
            return cursor.fetchone()
    
    @staticmethod
    def create(name):
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Categories (name) VALUES (%s) RETURNING id",
                [name]
            )
            return cursor.fetchone()[0]
    
    @staticmethod
    def update(category_id, name):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE Categories SET name = %s WHERE id = %s",
                [name, category_id]
            )
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(category_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Categories WHERE id = %s", [category_id])
            return cursor.rowcount > 0

class SQLStyleManager:
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM Styles ORDER BY id")
            return cursor.fetchall()
    
    @staticmethod
    def get_by_id(style_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM Styles WHERE id = %s", [style_id])
            return cursor.fetchone()
    
    @staticmethod
    def create(name):
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Styles (name) VALUES (%s) RETURNING id",
                [name]
            )
            return cursor.fetchone()[0]
    
    @staticmethod
    def update(style_id, name):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE Styles SET name = %s WHERE id = %s",
                [name, style_id]
            )
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(style_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Styles WHERE id = %s", [style_id])
            return cursor.rowcount > 0
