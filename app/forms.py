from flask_wtf import Form
from wtforms import StringField, BooleanField,SubmitField,PasswordField, DateTimeField,IntegerField,SelectField,RadioField,ValidationError,TextAreaField
from wtforms.validators import DataRequired
from app import db,models
from flask_login import current_user


class LoginForm(Form):
    username = StringField('用户名', render_kw={'placeholder': '输入用户名'}, description="请使用天津OTC股权交易系统用户名、及密码登陆.",validators=[DataRequired()])
    password = PasswordField('密码',render_kw={'placeholder': '输入密码'}, validators=[DataRequired()])
    remember_me = BooleanField('保持登陆', default=False)
    disclimaer = BooleanField('同意', default=True,validators=[DataRequired()])
    submit = SubmitField('登陆')


class PostForm(Form):
    lasting_days = SelectField('展示时间', choices = [(30, '30日'),(60, '60日'),(90, '90日')])
    postvalue = IntegerField('数量', render_kw={'placeholder': '输入股权数量'},validators=[DataRequired(message="数据错误"),])
    postdirection = RadioField('需求类型', choices = [(0,'转让需求'),(1,'购买需求')],validators=[DataRequired(message="请选择类型"),])
    disclimaer = BooleanField('同意', default=True, validators=[DataRequired()])
    remark = TextAreaField('附言')
    submit = SubmitField('发布')

    def validate_postvalue(self,field):
        if self.postdirection.data == '0':
            try:

                user = models.User.query.filter_by(username = current_user.username).first()
                mount = float(user.value_usble)

                user_id = user.id
                print("user_id %d ,mount %d",user_id,mount)
                sqlstr = "select sum(posts.post_value) as pvsum from posts where posts.post_direction=0 and posts.status=1 and posts.post_type_id in (1,2) and posts.userid="+ str(user_id)
                print(sqlstr)
                x = db.engine.execute(sqlstr).first()
                postvalue = self.postvalue.data

                temp_value = 0
                if x[0] is not None:
                    temp_value = x[0]
                if (mount-temp_value) < postvalue:
                    self.postvalue.errors += (ValidationError('可转让数量不足'),)
            except:
                self.postvalue.errors += (ValidationError('可转让数量不足1'),)


class EditForm(Form):
    pass
