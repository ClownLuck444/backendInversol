from . import db

class WH_ItemSerie(db.Model):
    __tablename__ = 'wh_itemserie'

    item = db.Column(db.Integer, primary_key=True)
    NumeroSerie = db.Column(db.String(100), nullable=False)
