import math
from ipaddress import ip_network, ip_address
from django.conf import settings

def validar_ip_universidade(ip_cliente):
    for network in settings.UNIVERSIDADE_IP_RANGES:
        if ip_address(ip_cliente) in ip_network(network):
            return True
    return False

def calcular_distancia(lat1, lon1, lat2, lon2):
    """Calcula a distância em metros entre dois pontos coordenados."""
    R = 6371000  # Raio da Terra em metros
    phi1, phi2 = math.radians(float(lat1)), math.radians(float(lat2))
    dphi = math.radians(float(lat2) - float(lat1))
    dlambda = math.radians(float(lon2) - float(lon1))

    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c