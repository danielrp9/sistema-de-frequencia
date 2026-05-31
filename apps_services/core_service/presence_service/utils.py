import math
from ipaddress import ip_address, ip_network
from django.conf import settings


def get_client_ip(request):
    """
    Captura o IP real do usuário.

    Quando o sistema está atrás de proxy, o IP pode vir em HTTP_X_FORWARDED_FOR.
    Caso contrário, usamos REMOTE_ADDR.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def validar_ip_universidade(ip_cliente):
    """
    Verifica se o IP do aluno pertence a algum range permitido da universidade.
    """
    if not ip_cliente:
        return False

    try:
        ip = ip_address(ip_cliente)

        for network in settings.UNIVERSIDADE_IP_RANGES:
            if ip in ip_network(network, strict=False):
                return True

        return False

    except ValueError:
        return False


def calcular_distancia(lat1, lon1, lat2, lon2):
    """
    Calcula a distância em metros entre dois pontos usando a fórmula de Haversine.
    """
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    raio_terra = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return raio_terra * c


def validar_geolocalizacao(lat_aluno, lon_aluno, sala):
    """
    Verifica se o aluno está dentro do raio permitido da sala.
    """
    if lat_aluno is None or lon_aluno is None:
        return False, None

    distancia = calcular_distancia(
        lat_aluno,
        lon_aluno,
        sala.latitude,
        sala.longitude,
    )

    dentro_do_raio = distancia <= sala.raio_permitido

    return dentro_do_raio, distancia