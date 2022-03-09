from django import forms

# 表单验证类
class Form(forms.Form):
    username = forms.CharField(max_length=16, required=True, error_messages={
        'max_length': '用户名太长了（超过16给了）',
        'required': '用户名不能为空'
    })
    password = forms.CharField(min_length=2, required=True, error_messages={
        'min_length': '密码太短',
        'required': '密码不能为空'
    })
