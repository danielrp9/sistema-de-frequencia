from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from academic.models import Course, Department, Disciplina, Sala, Turma
from classes.models import Aula
from presence_service.models import Presenca
from users.models import User


class DashboardGraficosTests(TestCase):
    def setUp(self):
        self.professor_user = User.objects.create_user(
            username='prof-dashboard',
            email='prof-dashboard@example.com',
            password='senha-forte-123',
            is_professor=True,
        )
        self.aluno_user = User.objects.create_user(
            username='aluno-dashboard',
            email='aluno-dashboard@example.com',
            password='senha-forte-123',
            is_aluno=True,
        )
        department = Department.objects.create(name='Computacao', code='DCC-DASH')
        course = Course.objects.create(name='Sistemas', department=department)
        self.disciplina = Disciplina.objects.create(
            nome='Sistemas Distribuidos',
            codigo='SD',
            course=course,
            carga_horaria_total=60,
        )
        self.turma = Turma.objects.create(
            disciplina=self.disciplina,
            professor=self.professor_user.perfil_professor,
            semestre='2026.1',
            ativa=True,
        )
        self.turma.alunos.add(self.aluno_user.perfil_aluno)
        self.sala = Sala.objects.create(
            nome='Lab 1',
            predio='Predio 1',
            latitude=-18.241234,
            longitude=-43.601234,
            raio_permitido=50,
        )
        agora = timezone.localtime()
        self.aula = Aula.objects.create(
            turma=self.turma,
            sala=self.sala,
            data=agora.date(),
            horario_inicio=agora.time(),
            horario_fim=(agora + timedelta(hours=2)).time(),
            peso_aula=2,
        )
        Presenca.objects.create(
            aluno=self.aluno_user.perfil_aluno,
            aula=self.aula,
            ip_registrado='127.0.0.1',
            latitude=-18.241234,
            longitude=-43.601234,
        )

    def test_dashboard_professor_renderiza_graficos_de_turma(self):
        self.client.force_login(self.professor_user)
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'dashboard-chart-data')
        self.assertContains(response, 'turmasChart')
        self.assertContains(response, 'resumoChart')

    def test_dashboard_aluno_renderiza_graficos_de_frequencia(self):
        self.client.force_login(self.aluno_user)
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'dashboard-chart-data')
        self.assertContains(response, 'frequenciaChart')
        self.assertContains(response, 'horasChart')
