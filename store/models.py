from django.db import models
from category.models import Category

# Create your models here.

class product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500,blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    # category being an foreign key related to the category class
    # on_delete = models.CASCADE - deletes all products that are related to the foreign key when it would be deleted
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    
    created_date = models.DateTimeField(auto_now_add = True)
    modified_date = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.product_name
    
