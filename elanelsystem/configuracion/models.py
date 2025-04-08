from django.db import models

# Create your models here.
class Configuracion(models.Model):
    clave = models.CharField(max_length=100, unique=True)
    valor = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.clave}: {self.valor}"