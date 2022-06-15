from django.db import models
class Item(models.Model):
    item_code=models.CharField(max_length=150)
    description=models.CharField(max_length=150)

def __str__(self):
    return f'{self.item_code}{self.description}'

# Create your models here.
