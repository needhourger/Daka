from . import auth
from .forms import LoginForm,RegisterForm
from ..models import User
from .. import db

from flask_login import login_user,logout_user,login_required,current_user
from flask import flash,redirect,url_for,render_template,request

@auth.route("/login",methods=["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(url_for("main.clock"))
        flash("错误的用户名或者密码")
    return render_template("auth/login.html",form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("账户注销成功")
    return redirect(url_for("main.index"))

@auth.route("/register",methods=["GET","POST"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,password=form.password0.data,nickname=form.nickname.data)
        db.session.add(user)
        db.session.commit()
        flash("注册成功")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html",form=form)
     

