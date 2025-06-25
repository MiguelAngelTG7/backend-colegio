from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate

from .models import User, Alumno, Padre, Curso, Nota, Salon


# --- Login ---
class LoginView(APIView):
    def post(self, request):
        print("HEADERS:", request.headers)
        print("BODY:", request.body)
        print("DATA:", request.data)
        
        username = request.data.get("username")
        password = request.data.get("password")
        
        print("Username:", username, "Password:", password)  # Para verificar si vienen vacíos
        
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "token": str(refresh.access_token),
                "role": user.role
            })
        return Response({"error": "Credenciales inválidas"}, status=401)


# --- Dashboard Profesor ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_profesor(request):
    if request.user.role != 'profesor':
        return Response({"error": "No autorizado"}, status=403)

    cursos = Curso.objects.filter(profesor=request.user).prefetch_related("salones")
    data = []

    for curso in cursos:
        grados_dict = {}
        for salon in curso.salones.all():
            alumnos = Alumno.objects.filter(salon=salon)
            nombres = []
            ids = []
            notas_alumno = []

            for alumno in alumnos:
                nombres.append(alumno.user.username)
                ids.append(alumno.id)
                try:
                    nota = Nota.objects.get(alumno=alumno, curso=curso)
                    notas_alumno.append([nota.nota1, nota.nota2, nota.nota3, nota.nota4])
                except Nota.DoesNotExist:
                    notas_alumno.append([])

            if salon.grado.nombre not in grados_dict:
                grados_dict[salon.grado.nombre] = []

            grados_dict[salon.grado.nombre].append({
                "seccion": salon.seccion,
                "alumnos": nombres,
                "alumno_ids": ids,
                "notas_previas": notas_alumno
            })

        data.append({
            "curso": curso.nombre,
            "curso_id": curso.id,
            "grados": grados_dict
        })

    return Response({"cursos": data})

# --- Registrar Nota ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_nota(request):
    if request.user.role != 'profesor':
        return Response({"error": "No autorizado"}, status=403)

    alumno_id = request.data.get("alumno_id")
    curso_id = request.data.get("curso_id")
    notas = request.data.get("notas", [])

    if not (alumno_id and curso_id and len(notas) == 4):
        return Response({"error": "Datos incompletos"}, status=400)

    try:
        alumno = Alumno.objects.get(id=alumno_id)
        curso = Curso.objects.get(id=curso_id)

        if curso.profesor != request.user:
            return Response({"error": "No autorizado para este curso"}, status=403)

        if alumno.salon not in curso.salones.all():
            return Response({"error": "Este alumno no pertenece al curso"}, status=403)

        nota_obj, created = Nota.objects.update_or_create(
            alumno=alumno,
            curso=curso,
            defaults={
                "nota1": notas[0],
                "nota2": notas[1],
                "nota3": notas[2],
                "nota4": notas[3],
            }
        )

        promedio = round((nota_obj.nota1 + nota_obj.nota2 + nota_obj.nota3 + nota_obj.nota4) / 4, 2)

        return Response({
            "mensaje": "Notas registradas correctamente",
            "notas_actualizadas": [nota_obj.nota1, nota_obj.nota2, nota_obj.nota3, nota_obj.nota4],
            "promedio": promedio
        })

    except Alumno.DoesNotExist:
        return Response({"error": "Alumno no encontrado"}, status=404)
    except Curso.DoesNotExist:
        return Response({"error": "Curso no encontrado"}, status=404)


# --- Dashboard Alumno ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_alumno(request):
    if request.user.role != 'alumno':
        return Response({"error": "No autorizado"}, status=403)

    try:
        alumno = Alumno.objects.get(user=request.user)
        notas = Nota.objects.filter(alumno=alumno).select_related("curso")

        data = []
        for n in notas:
            promedio = round((n.nota1 + n.nota2 + n.nota3 + n.nota4) / 4, 2)
            data.append({
                "curso": n.curso.nombre,
                "notas": [n.nota1, n.nota2, n.nota3, n.nota4],
                "promedio": promedio
            })

        return Response({
            "alumno": alumno.user.username,
            "notas": data
        })

    except Alumno.DoesNotExist:
        return Response({"error": "Alumno no encontrado"}, status=404)


# --- Dashboard Padre ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_padre(request):
    if request.user.role != 'padre':
        return Response({"error": "No autorizado"}, status=403)

    try:
        padre = Padre.objects.get(user=request.user)
        hijos_info = []

        for alumno in padre.alumnos.all():
            notas = Nota.objects.filter(alumno=alumno).select_related("curso")
            notas_info = []

            for n in notas:
                promedio = round((n.nota1 + n.nota2 + n.nota3 + n.nota4) / 4, 2)
                notas_info.append({
                    "curso": n.curso.nombre,
                    "notas": [n.nota1, n.nota2, n.nota3, n.nota4],
                    "promedio": promedio
                })

            hijos_info.append({
                "alumno": alumno.user.username,
                "notas": notas_info
            })

        return Response({
            "padre": padre.user.username,
            "hijos": hijos_info
        })

    except Padre.DoesNotExist:
        return Response({"error": "Padre no encontrado"}, status=404)
