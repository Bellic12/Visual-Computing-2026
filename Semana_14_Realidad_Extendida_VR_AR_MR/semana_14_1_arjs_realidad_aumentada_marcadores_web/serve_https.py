"""Servidor HTTPS local para la app AR (la cámara web exige contexto seguro).

Uso:
    python serve_https.py

Sirve la carpeta threejs/ en https://0.0.0.0:8443 con el certificado
autofirmado de .certs/. Desde el celular (misma WiFi) abre:
    https://<IP-del-PC>:8443/
y acepta la advertencia de certificado (es autofirmado, es normal).
"""
import http.server
import ssl
import os

PORT = 8443
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "threejs")
CERT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".certs", "cert.pem")
KEY = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".certs", "key.pem")

os.chdir(ROOT)

handler = http.server.SimpleHTTPRequestHandler
httpd = http.server.HTTPServer(("0.0.0.0", PORT), handler)

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(certfile=CERT, keyfile=KEY)
httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

print(f"Sirviendo {ROOT} en https://0.0.0.0:{PORT}/")
print("PC:     https://localhost:8443/")
print("Celular: https://192.168.1.19:8443/  (acepta la advertencia de certificado)")
httpd.serve_forever()
