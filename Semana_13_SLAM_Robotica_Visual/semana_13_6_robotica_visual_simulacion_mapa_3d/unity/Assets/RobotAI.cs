using UnityEngine;

public class RobotAI : MonoBehaviour
{
    [Header("Configuración de Movimiento")]
    public float speed = 3f;
    public float rotationSpeed = 120f; // Un poco más rápido para salir del apuro
    public float detectionDistance = 4f;
    public float safetyMargin = 0.8f; // Distancia mínima para no incrustarse en los muros

    [Header("Visualización")]
    public LineRenderer trailRenderer;

    private bool haLlegadoALaMeta = false;
    private bool estaGirando = false;

    [Header("Configuración de Capas")]
    public LayerMask capaObstaculos; // Esto aparecerá en el inspector

    void Update()
    {
        if (haLlegadoALaMeta) return;

        Vector3 rayOrigin = transform.position + Vector3.up * 0.2f;

        // Ahora el Raycast incluye al final 'capaObstaculos', ignorando todo lo demás (como la Meta)
        bool obstaculoDetectado = Physics.Raycast(rayOrigin, transform.forward, out RaycastHit hit, detectionDistance, capaObstaculos);

        if (obstaculoDetectado)
        {
            Debug.DrawLine(rayOrigin, hit.point, Color.red);

            if (hit.distance < safetyMargin || estaGirando)
            {
                estaGirando = true;
                transform.Rotate(0, rotationSpeed * Time.deltaTime, 0);
            }
            else
            {
                transform.Translate(Vector3.forward * (speed * 0.5f) * Time.deltaTime);
            }
        }
        else
        {
            estaGirando = false;
            Debug.DrawRay(rayOrigin, transform.forward * detectionDistance, Color.green);
            transform.Translate(Vector3.forward * speed * Time.deltaTime);
        }

        ActualizarRastro();
    }

    private void ActualizarRastro()
    {
        if (trailRenderer != null && trailRenderer.positionCount > 0)
        {
            // Evita registrar puntos si el robot casi no se ha movido
            if (Vector3.Distance(trailRenderer.GetPosition(trailRenderer.positionCount - 1), transform.position) > 0.1f)
            {
                trailRenderer.positionCount++;
                trailRenderer.SetPosition(trailRenderer.positionCount - 1, transform.position);
            }
        }
        else if (trailRenderer != null && trailRenderer.positionCount == 0)
        {
            trailRenderer.positionCount = 1;
            trailRenderer.SetPosition(0, transform.position);
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Meta") || other.gameObject.name == "Meta")
        {
            haLlegadoALaMeta = true;
            Debug.Log("Meta alcanzada");
        }
    }
}