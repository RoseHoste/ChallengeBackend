from Flask_framework import db

class NewRelease(db.Model):
    __tablename__ = "NewReleases"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable = False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id, 
            'name': self.name,
        }
