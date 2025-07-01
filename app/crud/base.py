def create(model, db, data):
    item = model(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_by(model, db, criteria=None, order=None):
    query = db.query(model)
    if criteria is not None:
        query = query.filter(criteria)
    if order is not None:
        query = query.order_by(order)

    return query.all()

