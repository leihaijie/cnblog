from django import forms
from django.forms import widgets
from .models import UserInfo
from django.core.exceptions import ValidationError


class RegForm(forms.Form):
    user = forms.CharField(max_length=8, label="用户名",
                           widget=widgets.TextInput(attrs={"class": "form-control"})
                           )
    pwd = forms.CharField(min_length=4, label="密码",
                          widget=widgets.PasswordInput(attrs={"class": "form-control"})
                          )
    repeat_pwd = forms.CharField(min_length=4, label="确认密码",
                                 widget=widgets.PasswordInput(attrs={"class": "form-control"})
                                 )
    email = forms.EmailField(label="邮箱",
                             widget=widgets.EmailInput(attrs={"class": "form-control"})
                             )

    def clean_user(self):
        value = self.cleaned_data.get("user")
        ret = UserInfo.objects.filter(username=value)
        if not ret:
            return value
        else:
            raise ValidationError("该用户已存在")

    def clean(self):
        if self.cleaned_data.get("pwd") == self.cleaned_data.get("repeat_pwd"):
            return self.cleaned_data
        else:
            self.add_error("repeat_pwd",ValidationError("两次密码不一致"))

