from math import sqrt

class AsignadorEspacios:
    def __init__(self, espacios):
        self.espacios = espacios

    def obtener_ocupados(self, vehiculos):
        ocupados = set()

        for vx, vz in vehiculos:
            mejor_id = None
            mejor_distancia = float('inf')

            for espacio_id, ex, ez in self.espacios:
                distancia = sqrt(
                    (vx - ex) ** 2 +
                    (vz - ez) ** 2
                )

                if distancia < mejor_distancia:
                    mejor_distancia = distancia
                    mejor_id = espacio_id
            
            if mejor_id:
                ocupados.add(mejor_id)
        
        return ocupados
