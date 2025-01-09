class Wheel:
    def __init__(self, id=None, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def get_all(db):
        cursor = db.execute('SELECT * FROM Wheels')
        wheels = cursor.fetchall()
        return [Wheel(w['id'], w['name'], w['description']) for w in wheels]

    @staticmethod
    def get_by_id(db, wheel_id):
        cursor = db.execute('SELECT * FROM Wheels WHERE id = ?', (wheel_id,))
        wheel = cursor.fetchone()
        if wheel:
            return Wheel(wheel['id'], wheel['name'], wheel['description'])
        return None

    def save(self, db):
        if self.id is None:
            cursor = db.execute(
                'INSERT INTO Wheels (name, description) VALUES (?, ?)',
                (self.name, self.description)
            )
            self.id = cursor.lastrowid
            db.commit()
        else:
            db.execute(
                'UPDATE Wheels SET name = ?, description = ? WHERE id = ?',
                (self.name, self.description, self.id)
            )
            db.commit()


    