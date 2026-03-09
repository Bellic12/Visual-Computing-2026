using UnityEngine;

public class CameraRotationSlider : MonoBehaviour
{
    [Header("Configuración de Rotación")]
    [Tooltip("Objetivo")]
    public Transform target;

    [Tooltip("Distancia de la cámara al objetivo")]
    public float distance = 10.0f;

    [Tooltip("Altura de la cámara respecto al objetivo")]
    public float height = 5.0f;

    [Space]
    [Header("Angulo de rotacion")]
    [Range(0f, 360f)]
    public float rotationAngle = 0f;
    void OnValidate()
    {
        UpdateCameraPosition();
    }

    void LateUpdate()
    {
        UpdateCameraPosition();
    }

    void UpdateCameraPosition()
    {
        if (target == null) return;
        float x = Mathf.Sin(rotationAngle * Mathf.Deg2Rad) * distance;
        float z = Mathf.Cos(rotationAngle * Mathf.Deg2Rad) * distance;

        Vector3 newPos = new Vector3(x, height, z) + target.position;
        
        transform.position = newPos;
        transform.LookAt(target.position);
    }
}