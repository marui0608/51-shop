from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import Form, StringField, PasswordField, SelectField, FileField, DecimalField, RadioField, TextField, \
    SubmitField
from wtforms.validators import Length, InputRequired, DataRequired


# 管理员登录表单
class AdminLoginForm(Form):
    manager = StringField(validators=[InputRequired(message='账号必填'), Length(0, 100, message='长度错误')])
    password = PasswordField(validators=[InputRequired(message='密码必填'), Length(0, 100, message='长度错误')])


# 添加修改商品
class AdminGoodsForm(FlaskForm):
    name = StringField(validators=[DataRequired('商品名称不能为空')])
    supercat = SelectField(validators=[DataRequired('大分类不能为空')], coerce=int)
    subcat = SelectField(validators=[DataRequired('小分类不能为空')], coerce=int)
    picture = FileField(validators=[FileRequired('图片不能为空'), FileAllowed(['jpg', 'png', 'gif'], message='头像格式错误')])
    old_price = DecimalField(validators=[DataRequired('商品原价格式错误')])
    new_price = DecimalField(validators=[DataRequired('商品现价格式错误')])
    is_new = RadioField(validators=[DataRequired('请选择是否新品')], coerce=int, choices=[(0, '否'), (1, '是')], default=0)
    is_sale = RadioField(validators=[DataRequired('请选择是否特价')], coerce=int, choices=[(0, '否'), (1, '是')], default=0)
    intro = TextField(validators=[DataRequired('商品简介不能为空')])
    submit = SubmitField(render_kw={'value': '提交'})
