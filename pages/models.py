from django.db import models

# Create your models here.
class BannerModel(models.Model):
    title = models.CharField(max_length=64)
    header = models.CharField(max_length=60)
    description = models.TextField()
    image = models.ImageField(upload_to="banners")
    is_active = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.header}: {self.title}"
    
    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        
        
class ContactModel(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.first_name}: {self.last_name} - {self.email}"
    
    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"