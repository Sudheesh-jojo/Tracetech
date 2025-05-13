from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Lost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    item_name = models.CharField(max_length=30)
    location = models.CharField(max_length=25)
    category = models.CharField(max_length=20)
    item_desc = models.CharField(max_length=100)
    image_url = models.URLField(blank=True,null=True)
    date=models.DateField()

    def __str__(self):
        return self.item_name


class Found(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    item_name = models.CharField(max_length=30)
    location = models.CharField(max_length=25)
    category = models.CharField(max_length=20)
    item_desc = models.CharField(max_length=100)
    image_url = models.URLField(blank=True,null=True)
    date=models.DateField()

    def __str__(self):
        return self.item_name

class MatchedItem(models.Model):
    lost_item = models.ForeignKey(Lost, on_delete=models.CASCADE)
    found_item = models.ForeignKey(Found, on_delete=models.CASCADE)
    is_collected = models.BooleanField(default=False)
    date=models.DateField(default=timezone.now)
    collected_by = models.CharField(max_length=255)
    


    def __str__(self):
        return f"Match: {self.lost_item} & {self.found_item}"

