import sqlite3

class Field:
    def __init__(self, field_type):
        self.field_type = field_type

class StringField(Field):
    def __init__(self, max_length=255):
        super().__init__(f"VARCHAR({max_length})")

class IntegerField(Field):
    def __init__(self):
        super().__init__("INTEGER")

class ModelMeta(type):
    def __new__(cls, name, bases, dct):
        fields = {key: value for key, value in dct.items() if isinstance(value, Field)}
        dct["_fields"] = fields
        cls_obj = super().__new__(cls, name, bases, dct)
        return cls_obj

class Model(metaclass=ModelMeta):
    _connection = sqlite3.connect(":memory:")

    def __init__(self, **kwargs):
        for field_name in self._fields.keys():
            setattr(self, field_name, kwargs.get(field_name))

    @classmethod
    def create_table(cls):
        fields = [f"{name} {field.field_type}" for name, field in cls._fields.items()]
        query = f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} ({', '.join(fields)})"
        cls._connection.execute(query)

    def save(self):
        field_names = ", ".join(self._fields.keys())
        placeholders = ", ".join(["?"] * len(self._fields))
        values = [getattr(self, name) for name in self._fields.keys()]
        query = f"INSERT INTO {self.__class__.__name__.lower()} ({field_names}) VALUES ({placeholders})"
        self._connection.execute(query, values)
        self._connection.commit()

    @classmethod
    def all(cls):
        query = f"SELECT * FROM {cls.__name__.lower()}"
        cursor = cls._connection.execute(query)
        return cursor.fetchall()

class User(Model):
    id = IntegerField()
    name = StringField(max_length=100)
    age = IntegerField()

User.create_table()

user1 = User(id=1, name="ALEX", age=30)
user1.save()

user2 = User(id=2, name="MORI", age=25)
user2.save()

users = User.all()
print("Entries", users)
