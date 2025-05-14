from .. import db
from datetime import datetime
from sqlalchemy import asc, desc

class Pin(db.Model):
    __tablename__ = 'pins'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    image_link = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "image_link": self.image_link,
            "date_created": self.date_created.isoformat(),
            "author": self.author
        }

    @classmethod
    async def get_all(cls, author_filter=None, order_by='date_created', order_dir='desc'):
        query = cls.query
        if author_filter:
            query = query.filter(cls.author.ilike(author_filter))
        
        order_func = desc if order_dir == 'desc' else asc
        query = query.order_by(order_func(getattr(cls, order_by)))
        
        return query.all()

    @classmethod
    async def get_by_id(cls, pin_id):
        return db.session.get(Pin, pin_id)

    @classmethod
    async def create(cls, pin_data):
        pin = cls(
            title=pin_data["title"],
            body=pin_data["body"],
            image_link=pin_data["image_link"],
            author=pin_data["author"],
            date_created=pin_data["date_created"]
        )
        db.session.add(pin)
        db.session.commit()
        return pin

    @classmethod
    async def update(cls, pin_id, pin_data):
        pin = db.session.get(Pin, pin_id)
        if pin:
            pin.title = pin_data["title"]
            pin.body = pin_data["body"]
            pin.image_link = pin_data["image_link"]
            pin.author = pin_data["author"]
            db.session.commit()
            return pin
        return None

    @classmethod
    async def delete(cls, pin_id):
        pin = db.session.get(Pin, pin_id)
        if pin:
            db.session.delete(pin)
            db.session.commit()
            return True
        return False