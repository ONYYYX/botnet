import sqlalchemy
from sqlalchemy import orm
from database.session import SqlAlchemyBase


class Role(SqlAlchemyBase):
    __tablename__ = 'roles'

    id = sqlalchemy.Column(sqlalchemy.Integer, index=True, primary_key=True, autoincrement=True)
    slug = sqlalchemy.Column(sqlalchemy.String(128), nullable=False, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String(128), nullable=False)
    styles = sqlalchemy.Column(sqlalchemy.String(256), nullable=True)
    cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    bots_limit = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=1)
    support_priority = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=1)
    users = orm.relationship('User', back_populates='role', lazy='subquery')
