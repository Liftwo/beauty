from django.db import models


class UserInfo(models.Model):
    username = models.CharField(verbose_name='用戶名', max_length=32)
    password = models.CharField(verbose_name='用戶密碼', max_length=64)
    token = models.CharField(verbose_name='用戶token', max_length=64, null=True, blank=True)
    email = models.CharField(verbose_name='信箱', max_length=32, default="@gmail")
    candidate = models.IntegerField(null=True)
    ig_account = models.CharField(verbose_name='ig帳號', max_length=32, default="account")
    ig_avatar = models.TextField(blank=True, null=True)
    # ig_photo = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.username


class IgPhoto(models.Model):  # 每位候選人皆有五張照片
    userinfo = models.ForeignKey(UserInfo, on_delete=models.CASCADE,null=True)
    username = models.CharField(verbose_name='用戶名', max_length=32, null=True)
    ig_photo = models.TextField(blank=True, null=True)
    visit = models.IntegerField(default=0)

    def __str__(self):
        return self.username

    def __str__(self):
        return str(self.visit)
