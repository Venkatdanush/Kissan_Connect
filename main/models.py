from django.db import models

class Farmer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Crop(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    farmer = models.ForeignKey(Farmer, related_name='crops', on_delete=models.CASCADE)
    planting_date = models.DateField()
    harvest_date = models.DateField()

    def __str__(self):
        return self.name

class Service(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='services/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(Farmer, related_name='blog_posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.name}'