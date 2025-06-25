from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Alumno, Padre, Curso, Nota, Grado, Salon

# Usuario personalizado
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Rol del sistema', {'fields': ('role',)}),
    )
    search_fields = ('username', 'email')

admin.site.register(User, UserAdmin)

# Alumno
@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('user', 'salon', 'get_grado')
    list_filter = ('salon__grado', 'salon__seccion')
    search_fields = ('user__username',)

    def get_grado(self, obj):
        return obj.salon.grado
    get_grado.short_description = 'Grado'

# Padre
@admin.register(Padre)
class PadreAdmin(admin.ModelAdmin):
    list_display = ('user', 'listar_hijos')
    search_fields = ('user__username',)

    def listar_hijos(self, obj):
        return ", ".join([a.user.username for a in obj.alumnos.all()])
    listar_hijos.short_description = "Hijos"

# Curso
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'listar_grados', 'profesor')
    search_fields = ('nombre',)

    def listar_grados(self, obj):
        grados = {s.grado.nombre for s in obj.salones.all()}
        return ", ".join(sorted(grados))
    listar_grados.short_description = 'Grado(s)'

# Nota
@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'curso', 'nota1', 'nota2', 'nota3', 'nota4', 'promedio')
    search_fields = ('alumno__user__username', 'curso__nombre')

    def promedio(self, obj):
        notas = [obj.nota1, obj.nota2, obj.nota3, obj.nota4]
        return round(sum(notas) / 4, 2)

# Grado y salón
admin.site.register(Grado)
admin.site.register(Salon)
