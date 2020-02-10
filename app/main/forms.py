
from ..models import User, Role

from datetime import datetime
from datetime import timedelta
from flask_wtf import FlaskForm

from wtforms import StringField
from wtfroms import PasswordField
from wtfroms import SubmitField
from wtforms import SelectField
from wtforms import DateTimeField
from wtforms import DateField

from wtforms.validators import Length
from wtforms.validators import Required
from wtforms.validators import EqualTo
from wtforms.validators import ValidationError
from wtforms.validators import Regexp


class AccountCenterForm(FlaskForm):
    new_nickname = StringField("修改真实姓名", validators=[
                               Length(1, 64, message="长度必须在64位以内")])
    submit = SubmitField("确认修改")

    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError("真实姓名已存在")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("旧密码", validators=[Required(), Length(6, 32)])
    password0 = PasswordField(
        "新的密码",
        validators=[
            Required(),
            Length(6, 32, message="长度必须为6-32位"),
            EqualTo("password1", message="两次输入密码不符")
        ],
        description="长度6-32位"
    )
    password1 = PasswordField(
        "重复一次",
        validators=[Required(), Length(6, 32, message="长度必须为6-32位")],
        description="长度6-32位"
    )
    submit = SubmitField("提交")


class AccountManagerAdminForm(FlaskForm):
    username = StringField(
        "用户名", validators=[Required(), Length(1, 64, message="最大长度64位")])
    nickname = StringField("真实姓名", validators=[
                           Required(), Length(1, 64, message="最大长度64位")])
    password = StringField("密码", description="6-32位")
    role = SelectField("Role", coerce=int)
    submit = SubmitField("提交")

    def __init__(self, user, *args, **kwargs):
        super(AccountManagerAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user


class RecordMakeUpForm(FlaskForm):
    datetime = DateTimeField(
        "补签时间", description="%Y-%m-%d %H:%M:%S", validators=[Required()])
    submit = SubmitField("补签")

    def validate_datetime(self, field):
        now = datetime.now()
        if field.data > now:
            raise ValidationError("错误的时间信息")


class AddUserAdminForm(FlaskForm):
    username = StringField(
        "用户名",
        validators=[
            Required(),
            Length(1, 64, message="长度必须在64位以内"),
            Regexp(
                "^(?!_)(?!.*?_$)[a-zA-Z0-9_\u4e00-\u9fa5]+$", 0, "用户名只可以包含数字字母下划线，减号")
        ],
        description="最大64位"
    )
    password0 = PasswordField(
        "密码",
        validators=[
            Required(),
            Length(6, 32, message="长度必须为6-32位"),
            EqualTo("password1", message="两次输入密码不符")
        ],
        description="长度6-32位"
    )
    password1 = PasswordField(
        "再输入一次",
        validators=[
            Required(),
            Length(6, 32, message="长度必须为6-32位")
        ],
        description="长度6-32位"
    )
    nickname = StringField("真实姓名", validators=[
                           Required(), Length(1, 64, message="长度必须在64位以内")])
    role = SelectField("Role", coerce=int)
    submit = SubmitField("提交")

    def __init__(self, *args, **kwargs):
        super(AddUserAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("用户名已存在")

    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError("真实姓名已存在")


class AddRecordAdminForm(FlaskForm):
    date = DateField("日期", description="%Y-%m-%d")
    clock_in = DateTimeField(
        "打卡时间", description="%Y-%m-%d %H:%M:%S", validators=[Required()])
    clock_out = DateTimeField(
        "签退时间", description="%Y-%m-%d %H:%M:%S", validators=[Required()])
    submit = SubmitField("确定")

    def validate_date(self, field):
        now = datetime.now()
        date = datetime.strptime(str(self.date.data), "%Y-%m-%d")
        if date > now:
            raise ValidationError("无法为未来添加记录")

    def validate_clock_in(self, field):
        today = datetime.strptime(str(self.date.data), "%Y-%m-%d")
        tomorrow = today+timedelta(days=1)
        if field.data < today or field.data > tomorrow:
            raise ValidationError("仅支持添加日期内的打卡记录")

    def validate_clock_out(self, field):
        today = datetime.strptime(str(self.date.data), "%Y-%m-%d")
        tomorrow = today+timedelta(days=1)
        if field.data < self.clock_in.data:
            raise ValidationError("签退时间不得早于打卡时间")
        if field.data > tomorrow:
            raise ValidationError("签退时间不得为次日之后")
