from sqlalchemy.orm import Session


class CRUDBase:
    def __init__(self, model):
        self.model = model

    def create(self, db: Session, data: dict):
        item = self.model(**data)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def get_by(self, db: Session, criteria=None, order=None):
        query = db.query(self.model)
        if criteria is not None:
            query = query.filter(criteria)
        if order is not None:
            query = query.order_by(order)
        return query.all()

    def get_first(self, db: Session, criteria=None):
        return db.query(self.model).filter(criteria).first()