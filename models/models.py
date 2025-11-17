from app import db

class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    chapter = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(10), nullable=True)
   

    def __repr__(self):
        return f"<Book {self.title}>"