from ..models import User

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms import Label

from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import Required
from wtforms.validators import Regexp
from wtforms.validators import EqualTo
from wtforms.validators import ValidationError


class LoginForm(FlaskForm):
    username = StringField("用户名", validators=[Required(), Length(1, 64)])
    password = PasswordField("密码", validators=[Required()])
    remember_me = BooleanField("记住我")
    submit = SubmitField("登录")


class RegisterForm(FlaskForm):
    username = StringField("用户名",
                           validators=[Required(), Length(1, 64, message="长度必须在64位以内"), Regexp(
                               "^(?!_)(?!.*?_$)[a-zA-Z0-9_\u4e00-\u9fa5]+$", 0, "用户名只可以包含数字字母下划线，减号")],
                           description="最大64位")
    password0 = PasswordField("密码", validators=[Required(), Length(
        6, 32, message="长度必须为6-32位"), EqualTo("password1", message="两次输入密码不符")], description="长度6-32位")
    password1 = PasswordField("再输入一次", validators=[Required(), Length(
        6, 32, message="长度必须为6-32位")], description="长度6-32位")
    nickname = StringField("真实姓名", validators=[
                           Required(), Length(1, 64, message="长度必须在64位以内")])
    submit = SubmitField("提交")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("用户名已存在")

    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError("真实姓名已存在")
