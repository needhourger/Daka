from . import db
from . import login_manager

import time
from datetime import datetime
from flask_sqlalchemy import event
from flask_login import UserMixin
from flask import current_app
from werkzeug import generate_password_hash,check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin,db.Model):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),unique=True,index=True)
    password_hash=db.Column(db.String(128))
    nickname=db.Column(db.String(64))
    role_id=db.Column(db.Integer,db.ForeignKey("roles.id"))
    records=db.relationship("Record",backref="user",lazy="dynamic")

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.username in current_app.config["ADMIN_LIST"]:
                self.role=Role.query.filter_by(permissions=Permission.ADMINISTER).first()
            if self.role is None:
                self.role=Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return "<User {} role {}>".format(self.username,self.role_id)

    def can(self,permissions):
        return self.role is not None and (self.role.permissions & permissions)==permissions

    def is_admin(self):
        return self.can(Permission.ADMINISTER)
    
    def is_clock_in(self):
        record=Record.query.filter_by(date=datetime.utcnow().strftime("%Y-%m-%d"),user_id=self.id).first()
        if record is None:
            return False
        return True

    def is_clock_out(self):
        record=Record.query.filter_by(date=datetime.utcnow().strftime("%Y-%m-%d"),user_id=self.id,clock_out=True).first()
        if record is None:
            return False
        return True

class Permission:
    VIEW_SELF=0x01
    VIEW_ALL=0x08
    ADMINISTER=0xff

class Role(db.Model):
    __tablename__="roles"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    default=db.Column(db.Boolean,default=False,index=True)
    permissions=db.Column(db.Integer)
    users=db.relationship("User",backref="role",lazy="dynamic")

    @staticmethod
    def insert_roles():
        roles={
            "Intern":(Permission.VIEW_SELF,True),
            "Staff":(Permission.VIEW_SELF,False),
            "Admin":(Permission.ADMINISTER,False)
        }
        for r in roles:
            role=Role.query.filter_by(name=r).first()
            if role is None:
                role=Role(name=r)
            role.permissions=roles[r][0]
            role.default=roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role {}>".format(self.name)

class Record(db.Model):
    __tablename__="records"
    id=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.Date,index=True)
    year=db.Column(db.Integer)
    month=db.Column(db.Integer)
    clock_in_time=db.Column(db.DateTime)
    clock_out_time=db.Column(db.DateTime)
    clock_out=db.Column(db.Boolean,default=False)
    hours=db.Column(db.Float,default=0)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"),index=True)

    def __repr__(self):
        return "<Record {} user_id {} clock_out {}>".format(self.date,self.user_id,self.clock_out)

@event.listens_for(Record.clock_out,"set")
def record_set_event(target,value,oldvalue,initiator):
    if value and not oldvalue:
        t1=target.clock_in_time
        t2=target.clock_out_time
        target.hours=(t2-t1).seconds/3600

@event.listens_for(Record,"before_insert")
def record_after_insert_event(mapper,connection,target):
    target.year=target.date.year
    target.month=target.date.month
    if target.clock_out:
        t1=target.clock_in_time
        t2=target.clock_out_time
        target.hours=(t2-t1).seconds/3600