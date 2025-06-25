from django.db import models
from django.contrib.auth.models import AbstractUser

# Usuario personalizado
class User(AbstractUser):
    ROLE_CHOICES = [
        ('profesor', 'Profesor'),
        ('alumno', 'Alumno'),
        ('padre', 'Padre'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

# Grado escolar (1° a 6°)
class Grado(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

# Salón por grado (A, B, etc.)
class Salon(models.Model):
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
    seccion = models.CharField(max_length=1)  # A, B

    def __str__(self):
        return f"{self.grado} - {self.seccion}"

# Curso relacionado directamente a un salón
class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    salones = models.ManyToManyField(Salon)  # <- aquí el cambio
    profesor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'profesor'})

    def __str__(self):
        return self.nombre


# Alumno
class Alumno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'alumno'})
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

# Padre de familia
class Padre(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'padre'})
    alumnos = models.ManyToManyField(Alumno)

    def __str__(self):
        return self.user.username

# Notas
class Nota(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    nota1 = models.DecimalField(max_digits=5, decimal_places=2)
    nota2 = models.DecimalField(max_digits=5, decimal_places=2)
    nota3 = models.DecimalField(max_digits=5, decimal_places=2)
    nota4 = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.alumno} - {self.curso}"
