from django.core.management.base import BaseCommand
from api.models import User, Grado, Salon, Alumno, Padre

class Command(BaseCommand):
    help = 'Crea un usuario con rol: alumno, profesor o padre'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True)
        parser.add_argument('--password', type=str, required=True)
        parser.add_argument('--rol', type=str, required=True, choices=['alumno', 'profesor', 'padre'])
        parser.add_argument('--grado', type=int, required=False)
        parser.add_argument('--seccion', type=str, required=False)

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        rol = options['rol']
        grado = options.get('grado')
        seccion = options.get('seccion')

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"❗ El usuario '{username}' ya existe."))
            return

        user = User.objects.create_user(username=username, password=password, role=rol, is_active=True)
        self.stdout.write(self.style.SUCCESS(f"✅ Usuario '{username}' ({rol}) creado."))

        if rol == 'alumno':
            if grado is None or seccion is None:
                self.stdout.write(self.style.ERROR("⚠️ Para alumnos debes proporcionar --grado y --seccion"))
                return

            try:
                salon = Salon.objects.get(grado__nombre=str(grado), seccion=seccion.upper())
            except Salon.DoesNotExist:
                self.stdout.write(self.style.ERROR("🚫 El salón especificado no existe."))
                return

            Alumno.objects.create(user=user, salon=salon)
            self.stdout.write(self.style.SUCCESS(f"🎓 Alumno asignado al salón {salon}"))

        elif rol == 'padre':
            Padre.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f"👨‍👩‍👧 Padre creado (sin alumnos asignados todavía)."))

        # Profesores no requieren extra
