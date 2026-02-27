using UnityEngine;
using UnityEngine.UI;

public class Projection : MonoBehaviour
{
    public Camera cam;

    [Header("Slider")]

    public Slider ortSize;

    public Button changePersOrt;

    void Start()
    {
        cam.orthographic = false;
        // Relacionar el boton con su función al oprimir
        changePersOrt.onClick.AddListener(CambiarModo);
        // Relacionar slider con su funcion
        ortSize.onValueChanged.AddListener(CambiarTamano);

        CambiarTamano(ortSize.value);
    }
    void CambiarTamano(float value)
    {
        if (cam.orthographic)
        {
            cam.orthographicSize = value;
        }
    }

    void CambiarModo()
    {
        if (cam.orthographic)
        {
            cam.orthographic = false;
        }else
        {
            cam.orthographic = true;
        }
    }
}