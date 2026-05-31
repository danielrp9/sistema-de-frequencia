import json
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from academic.models import Course, Department, Disciplina, Sala, Turma
from classes.models import Aula
from presence_service.models import Presenca
from users.models import User


class FluxoPrincipalPresencaTests(TestCase):
    def setUp(self):
        self.professor_user = User.objects.create_user(
            username='professor',
            email='professor@example.com',
            password='senha-forte-123',
            is_professor=True,
        )
        self.aluno_user = User.objects.create_user(
            username='aluno',
            email='aluno@example.com',
            password='senha-forte-123',
            is_aluno=True,
        )

        department = Department.objects.create(name='Computacao', code='DCC')
        course = Course.objects.create(name='Sistemas de Informacao', department=department)
        self.disciplina = Disciplina.objects.create(
            nome='Sistemas Distribuidos',
            codigo='DCC001',
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
            nome='Laboratorio 102',
            predio='Predio de Aulas 1',
            latitude=-18.241234,
            longitude=-43.601234,
            raio_permitido=50,
        )

    def test_professor_abre_aula_aluno_registra_api_relatorio_mostra_presenca(self):
        self.client.force_login(self.professor_user)

        response = self.client.post(
            reverse('registrar_aula'),
            {
                'turma': self.turma.id,
                'sala': self.sala.id,
                'peso_aula': 2,
            },
        )
        self.assertRedirects(response, reverse('dashboard'))

        aula = Aula.objects.get(turma=self.turma, sala=self.sala)
        self.assertTrue(aula.is_ativa())

        response = self.client.get(reverse('visualizar_qr_code', args=[aula.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertTrue(response.content.startswith(b'\x89PNG'))

        self.client.force_login(self.aluno_user)
        response = self.client.post(
            reverse('api_registrar_presenca'),
            data=json.dumps({
                'aula_id': aula.id,
                'token': str(aula.token_qr),
                'latitude': -18.241234,
                'longitude': -43.601234,
            }),
            content_type='application/json',
            REMOTE_ADDR='127.0.0.1',
        )

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()['sucesso'], True)
        self.assertEqual(response.json()['codigo'], 'PRESENCA_ENFILEIRADA')
        self.assertEqual(response.json()['dados']['aula_id'], aula.id)
        self.assertEqual(response.json()['dados']['disciplina'], self.disciplina.nome)
        self.assertTrue(Presenca.objects.filter(aluno=self.aluno_user.perfil_aluno, aula=aula).exists())

        self.client.force_login(self.professor_user)
        response = self.client.get(reverse('relatorio_presenca_disciplina', args=[self.turma.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.aluno_user.perfil_aluno.nome)
        self.assertContains(response, 'P')

    def test_api_retorna_contrato_padronizado_para_token_invalido(self):
        agora = timezone.localtime()
        aula = Aula.objects.create(
            turma=self.turma,
            sala=self.sala,
            peso_aula=2,
            data=agora.date(),
            horario_inicio=agora.time(),
            horario_fim=(agora + timedelta(hours=2)).time(),
        )

        self.client.force_login(self.aluno_user)
        response = self.client.post(
            reverse('api_registrar_presenca'),
            data=json.dumps({
                'aula_id': aula.id,
                'token': '00000000-0000-0000-0000-000000000000',
                'latitude': -18.241234,
                'longitude': -43.601234,
            }),
            content_type='application/json',
            REMOTE_ADDR='127.0.0.1',
        )

        body = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(body['sucesso'], False)
        self.assertEqual(body['codigo'], 'VALIDATION_ERROR')
        self.assertIn('mensagem', body)
        self.assertIn('erros', body)
