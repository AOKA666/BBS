from django import forms
from blog import models


class RegForm(forms.Form):

    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
        return forms.Form.__new__(cls)
    
    username = forms.CharField(label="用户名", min_length=3, max_length=8,error_messages={
        'min_length': '至少3位字符',
        'max_length': '最多8位字符',
        'required': '用户名不能为空'
    })
    email = forms.EmailField(label='邮箱', error_messages={
        'required': '邮箱不能为空',
        'invalid': '邮箱格式错误',
    }, widget=forms.EmailInput())
    password = forms.CharField(label='密码', min_length=6, error_messages={
        'min-length': '密码至少6位',
        'required': '密码不能为空'
    }, widget=forms.PasswordInput())

    password2 = forms.CharField(label='确认密码', min_length=6, error_messages={
        'min-length': '密码至少6位',
        'required': '密码不能为空'
    }, widget=forms.PasswordInput())

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username.startswith('_'):
            self.add_error('username', '用户名不能以下划线开头')
        return username

    def clean(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            self.add_error('password2', '两次密码必须一致')
        return self.cleaned_data
