from obtencion_coordenadas import main


class DetectorReal:
    def obtener_vehiculos(self):
        print("EJECUTANDO DETECTOR")
        try:
            coordenadas = main()
            return [
                (
                    x - 38.0,
                    y - 6.75
                )
                for x, y in coordenadas
            ]
        except Exception as e:
            print("Error detector:", e)
            return []