from django.db import models

class StoreSetting(models.Model):
    store_name = models.CharField(max_length=100, default='Velora')
    store_email = models.EmailField(default='hello@velora.com')
    phone = models.CharField(max_length=30, default='+230 1234-5678')
    currency = models.CharField(max_length=10, default='Rs MUR')
    timezone = models.CharField(max_length=100, default='(GMT +4:00) Mauritius Standard Time')
    legal_name = models.CharField(max_length=150, default='Velora Fashion LTD')
    description = models.TextField(blank=True, default='Velora is a modern fashion brand that offers a wide range of stylish clothing and accessories for men and women. Our mission is to provide high-quality fashion products that are both trendy and affordable, ensuring our customers look and feel their best.')
    address = models.CharField(max_length=255, default='123 Fashion Ave, 5th Floor')
    city = models.CharField(max_length=100, default='Rose Hill')
    state = models.CharField(max_length=100, default='Mauritius')

    class Meta:
        verbose_name = 'Store Setting'
        verbose_name_plural = 'Store Settings'

    def __str__(self):
        return self.store_name

    @classmethod
    def get_solo(cls):  #what for?
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj