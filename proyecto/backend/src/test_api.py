"""
Run from backend/src/:
    pytest test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient

from api import app, gestor_reservas

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_reservas():
    gestor_reservas.reset()
    yield
    gestor_reservas.reset()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /espacios
# ---------------------------------------------------------------------------

def test_espacios_devuelve_18_espacios():
    r = client.get("/espacios")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 18


def test_espacios_tiene_campos_requeridos():
    r = client.get("/espacios")
    for espacio in r.json():
        assert 'id' in espacio
        assert 'x' in espacio
        assert 'z' in espacio
        assert 'ocupado' in espacio
        assert 'reservado' in espacio


def test_espacios_sin_reservas_ninguno_reservado():
    r = client.get("/espacios")
    for espacio in r.json():
        assert espacio['reservado'] is False


# ---------------------------------------------------------------------------
# POST /reservar
# ---------------------------------------------------------------------------

def test_reservar_retorna_ruta_valida():
    r = client.post("/reservar?entrada=noroeste")
    assert r.status_code == 200
    data = r.json()
    assert data['ok'] is True
    assert 'espacio_id' in data
    assert isinstance(data['ruta'], list)
    assert len(data['ruta']) >= 2
    assert 'destino' in data
    assert data['destino'] is not None
    assert 'distancia' in data


def test_reservar_espacio_aparece_como_reservado_en_espacios():
    r = client.post("/reservar?entrada=noroeste")
    espacio_id = r.json()['espacio_id']

    espacios = client.get("/espacios").json()
    reservado = next(e for e in espacios if e['id'] == espacio_id)
    assert reservado['reservado'] is True


def test_reservar_espacio_no_esta_ocupado():
    r = client.post("/reservar?entrada=noroeste")
    espacio_id = r.json()['espacio_id']

    espacios = client.get("/espacios").json()
    espacio = next(e for e in espacios if e['id'] == espacio_id)
    assert espacio['ocupado'] is False


def test_dos_carros_no_comparten_espacio():
    """When at least one free space exists, two reservations must target different spaces."""
    r1 = client.post("/reservar?entrada=noroeste")
    assert r1.status_code == 200
    espacio_1 = r1.json()['espacio_id']

    r2 = client.post("/reservar?entrada=noreste")
    if r2.status_code == 200:
        espacio_2 = r2.json()['espacio_id']
        assert espacio_1 != espacio_2, "Dos carros fueron enviados al mismo espacio"
    else:
        # Only one free space existed — second car correctly got 409
        assert r2.status_code == 409


def test_segundo_reservar_cuando_no_hay_espacios_devuelve_409():
    """With simulation (1 free space), once it's reserved the next request should get 409."""
    r1 = client.post("/reservar?entrada=noroeste")
    assert r1.status_code == 200

    r2 = client.post("/reservar?entrada=sureste")
    assert r2.status_code == 409


def test_reservar_distintas_entradas_retorna_entrada_correcta():
    for entrada in ('noroeste', 'noreste', 'suroeste', 'sureste'):
        gestor_reservas.reset()
        r = client.post(f"/reservar?entrada={entrada}")
        if r.status_code == 200:
            assert r.json()['entrada'] == entrada
            break


# ---------------------------------------------------------------------------
# DELETE /reservar/{espacio_id}
# ---------------------------------------------------------------------------

def test_liberar_reserva():
    r = client.post("/reservar?entrada=sureste")
    assert r.status_code == 200
    espacio_id = r.json()['espacio_id']

    r2 = client.delete(f"/reservar/{espacio_id}")
    assert r2.status_code == 200
    assert r2.json()['ok'] is True

    espacios = client.get("/espacios").json()
    espacio = next(e for e in espacios if e['id'] == espacio_id)
    assert espacio['reservado'] is False


def test_liberar_espacio_no_reservado_no_falla():
    r = client.delete("/reservar/E-1-1")
    assert r.status_code == 200


def test_tras_liberar_se_puede_reservar_de_nuevo():
    r1 = client.post("/reservar?entrada=noroeste")
    assert r1.status_code == 200
    espacio_id = r1.json()['espacio_id']

    client.delete(f"/reservar/{espacio_id}")

    r2 = client.post("/reservar?entrada=noroeste")
    assert r2.status_code == 200


# ---------------------------------------------------------------------------
# GET /estado
# ---------------------------------------------------------------------------

def test_estado_incluye_version_reservas():
    r = client.get("/estado?entrada=noroeste")
    assert r.status_code == 200
    data = r.json()
    assert 'version_reservas' in data
    assert isinstance(data['version_reservas'], int)


def test_version_reservas_incrementa_al_reservar():
    v0 = client.get("/estado").json()['version_reservas']
    client.post("/reservar?entrada=noroeste")
    v1 = client.get("/estado").json()['version_reservas']
    assert v1 > v0


def test_version_reservas_incrementa_al_liberar():
    client.post("/reservar?entrada=noroeste")
    v0 = client.get("/estado").json()['version_reservas']

    espacios = client.get("/espacios").json()
    espacio_id = next(e['id'] for e in espacios if e['reservado'])
    client.delete(f"/reservar/{espacio_id}")

    v1 = client.get("/estado").json()['version_reservas']
    assert v1 > v0
