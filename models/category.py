class Category:
    def __init__(self, id=None, name=None, color=None):
        self.id = id
        self.name = name
        self.color = color or '#FFFFFF'

    @staticmethod
    def get_all(db):
        cursor = db.execute('SELECT * FROM Categories')
        categories = cursor.fetchall()
        return [Category(c['id'], c['name'], c['color']) for c in categories]

    @staticmethod
    def get_for_wheel(db, wheel_id):
        cursor = db.execute(
            '''
            SELECT c.id, c.name, c.color 
            FROM Categories c
            JOIN WheelCategories wc ON c.id = wc.category_id
            WHERE wc.wheel_id = ?
            ORDER BY wc.position
            ''',
            (wheel_id,)
        )
        # Return the results as dictionaries instead of Category objects
        return [
            {
                'id': row[0],
                'name': row[1],
                'color': row[2]
            }
            for row in cursor.fetchall()
        ]

    def save(self, db):
        if self.id is None:
            cursor = db.execute(
                'INSERT INTO Categories (name, color) VALUES (?, ?)',
                (self.name, self.color)
            )
            self.id = cursor.lastrowid
            db.commit()
        else:
            db.execute(
                'UPDATE Categories SET name = ?, color = ? WHERE id = ?',
                (self.name, self.color, self.id)
            )
            db.commit()
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color
        }