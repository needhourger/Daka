from app import db
from ..main import main
from .forms import AccountCenterForm,ResetPasswordForm,AccountManagerAdminForm,RecordMakeUpForm,AddUserAdminForm,AddRecordAdminForm
from ..decorateors import admin_required
from ..models import User,Role,Record,Permission

from datetime import datetime
from flask import render_template,flash,redirect,url_for,current_app,request
from flask_login import login_required,current_user
from sqlalchemy.sql import func

@main.route("/")
def index():
    return render_template("/main/index.html")

@main.route("/account_center",methods=["GET","POST"])
@login_required
def account_center():
    form=AccountCenterForm()
    if form.validate_on_submit():
        current_user.nickname=form.new_nickname.data
        db.session.add(current_user)
        db.session.commit()
    form.new_nickname.data=current_user.nickname
    return render_template("main/account_center.html",form=form)

@main.route("/reset_password",methods=["GET","POST"])
@login_required
def reset_password():
    form=ResetPasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            current_user.password=form.password0.data
            db.session.add(current_user)
            db.session.commit()
            flash("密码重置成功")
        else:
            flash("旧密码错误")
    return render_template("main/reset_password.html",form=form)

@main.route("/account_manager_admin/<int:id>",methods=["POST","GET"])
@login_required
@admin_required
def account_manager_admin(id=-1):
    users=User.query.filter(~User.username.in_(current_app.config["ADMIN_LIST"])).all()
    user=User.query.get(id)
    if user is None:
        user=User.query.filter(~User.username.in_(current_app.config["ADMIN_LIST"])).first()
    form=AccountManagerAdminForm(user=user)
    if form.validate_on_submit():
        user.username=form.username.data
        user.nickname=form.nickname.data
        user.role=Role.query.get(form.role.data)
        if len(form.password.data)>=6 and len(form.password.data)<=32:
            user.password=form.password.data
        db.session.add(user)
        db.session.commit()
        flash("信息更新成功")
        return render_template("main/account_manager_admin.html",form=form,users=users,user=user)
    form.username.data=user.username
    form.nickname.data=user.nickname
    form.role.data=user.role_id
    return render_template("main/account_manager_admin.html",form=form,users=users,user=user)


@main.route("/account_manager_admin/adduser",methods=["POST","GET"])
@login_required
@admin_required
def adduser_admin():
    form=AddUserAdminForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,nickname=form.nickname.data,password=form.password0.data,role=Role.query.get(form.role.data))
        db.session.add(user)
        db.session.commit()
        flash("用户添加成功")
        new_user=User.query.filter_by(username=form.username.data).first()
        return redirect(url_for("main.account_manager_admin",id=new_user.id))
    default_role=Role.query.filter_by(default=True).first()
    form.role.data=default_role.id
    return render_template("main/adduser_admin.html",form=form)


@main.route("/account_manager_admin/delete/<int:id>",methods=["POST","GET"])
@login_required
@admin_required
def account_delete(id=-1):
    user=User.query.filter_by(id=id).first()
    if user is None:
        flash("目标用户不存在，因而无法删除")
        return redirect(url_for("main.account_manager_admin",id=id+1))
    else:
        Record.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        flash("目标用户以及相关记录已被全部删除")
        return  redirect(url_for("main.account_manager_admin",id=id+1))


@main.route("/clock_in",methods=["POST","GET"])
@login_required
def clock_in():
    if not current_user.is_clock_in():
        record=Record(date=datetime.now(),clock_in_time=datetime.now(),user_id=current_user.id)
        db.session.add(record)
        db.session.commit()
        flash("打卡成功")
        return redirect(url_for("main.clock"))
    flash("您今日已完成打卡")
    return redirect(url_for("main.clock"))



@main.route("/clock_out")
@login_required
def clock_out():
    if not current_user.is_clock_out():
        record=Record.query.filter_by(date=datetime.now().strftime("%Y-%m-%d"),clock_out=False,user_id=current_user.id).first()
        if record is None:
            flash("未能查询到您的打卡记录无法完成签退")
            return redirect(url_for("main.clock"))
        record.clock_out_time=datetime.now()
        record.clock_out=True
        db.session.add(record)
        db.session.commit()
        flash("签退成功")
        return redirect(url_for("main.clock"))
    flash("您今日已经完成签退")
    return redirect(url_for("main.clock"))


    
@main.route("/clock")
@login_required
def clock():
    return render_template("main/clock.html")

def generate_summary_data(user):
    ret=[]
    user_query=Record.query.filter_by(user=user)
    years=user_query.with_entities(func.distinct(Record.year)).all()
    for year in years:
        months=user_query.filter_by(year=year[0]).with_entities(func.distinct(Record.month)).all()
        for month in months:
            node={
                "year":year[0],
                "month":month[0],
                "worktime":user_query.filter_by(year=year[0],month=month[0]).with_entities(func.sum(Record.hours)).first()[0]
            }
            ret.append(node)
    return ret

@main.route("/record")
@login_required
def record():
    year=request.args.get("year",0)
    month=request.args.get("month",0)
    user=User.query.filter_by(id=current_user.id).first()
    data=generate_summary_data(user)
    worktime=Record.query.filter_by(user=user).with_entities(func.sum(Record.hours)).first()[0]
    records=Record.query.filter_by(user=user,year=year,month=month).order_by(Record.date.desc()).all()
    return render_template("main/record.html",records=enumerate(records),data=data,worktime=worktime)
        

@main.route("/record_admin/<int:id>")
@login_required
@admin_required
def record_admin(id=-1):
    if id==-1:
        id=current_user.id
    year=request.args.get("year",0)
    month=request.args.get("month",0)
    users=User.query.all()
    user=User.query.filter_by(id=id).first()
    worktime=Record.query.filter_by(user=user).with_entities(func.sum(Record.hours)).first()[0]
    data=generate_summary_data(user)
    records=Record.query.filter_by(user=user,year=year,month=month).order_by(Record.date.desc()).all()
    return render_template("main/record_admin.html",users=users,records=enumerate(records),user=user,worktime=worktime,data=data)

@main.route("/record_admin/delete/<int:id>")
@login_required
@admin_required
def record_delete(id):
    record=Record.query.filter_by(id=id).first()
    if record is None:
        flash("目标记录不存在，无法完成删除操作")
        return redirect(url_for("main.record_admin",id=current_user.id))
    else:
        user_id=record.user_id
        db.session.delete(record)
        db.session.commit()
        return redirect(url_for("main.record_admin",id=user_id))

@main.route("/record_admin/addrecord/<int:id>",methods={"GET","POST"})
@login_required
@admin_required
def add_record(id):
    user=User.query.filter_by(id=id).first()
    if user is None:
        flash("该用户不存在，无法为其添加记录")
        return redirect(url_for("main.record_admin",id=-1))
    form=AddRecordAdminForm()
    if form.validate_on_submit():
        record=Record(date=form.date.data,clock_in_time=form.clock_in.data,clock_out_time=form.clock_out.data,clock_out=True,user_id=id)
        db.session.add(record)
        db.session.commit()
        flash("记录添加成功")
        return redirect(url_for("main.record_admin",id=id))
    form.date.data=datetime.now()
    form.clock_in.data=datetime.now()
    form.clock_out.data=datetime.now()
    return render_template("main/addrecord.html",form=form,user=user)


@main.route("/record_admin/makeup/<int:id>",methods=["GET","POST"])
@login_required
@admin_required
def record_makeup(id):
    record=Record.query.filter_by(id=id).first()
    if record is None:
        flash("目标记录不存在，无法完成补签")
        return redirect(url_for("main.record_admin",id=current_user.id))
    user=User.query.filter_by(id=record.user_id).first()
    form=RecordMakeUpForm()
    if form.validate_on_submit():
        record.clock_out_time=form.datetime.data
        record.clock_out=True
        db.session.add(record)
        db.session.commit()
        flash("补签成功")
        return redirect(url_for("main.record_admin",id=user.id))
    form.datetime.data=record.clock_in_time        
    return render_template("main/record_makeup.html",form=form,record=record,user=user)
