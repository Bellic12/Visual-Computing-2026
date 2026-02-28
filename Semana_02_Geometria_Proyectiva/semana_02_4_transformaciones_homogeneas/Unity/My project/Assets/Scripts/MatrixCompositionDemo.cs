using UnityEngine;

public class MatrixCompositionDemo : MonoBehaviour
{
    [Header("Markers (world positions)")]
    public Transform markerTR; // punto resultado de (T*R)*p
    public Transform markerRT; // punto resultado de (R*T)*p

    [Header("Point in homogeneous coordinates (local)")]
    public Vector3 localPoint = new Vector3(1f, 0f, 0f);

    [Header("Transform parameters")]
    public Vector3 translation = new Vector3(1f, 0f, 0f);
    public Vector3 rotationEuler = new Vector3(0f, 45f, 0f);

    [Header("Animation")]
    public bool animate = true;
    public float rotSpeedDegPerSec = 30f;

    private void Update()
    {
        // Rotación animada (solo para que se vea dinámico)
        Vector3 euler = rotationEuler;
        if (animate)
            euler.y += Time.time * rotSpeedDegPerSec;

        // Matrices homogéneas 4x4
        Matrix4x4 T = Matrix4x4.Translate(translation);
        Matrix4x4 R = Matrix4x4.Rotate(Quaternion.Euler(euler));

        // Punto homogéneo (x,y,z,1)
        Vector4 p = new Vector4(localPoint.x, localPoint.y, localPoint.z, 1f);

        // Composición 1: T * R
        Vector4 pTR = (T * R) * p;

        // Composición 2: R * T
        Vector4 pRT = (R * T) * p;

        // Ubicar marcadores en el mundo con los resultados
        if (markerTR != null) markerTR.position = new Vector3(pTR.x, pTR.y, pTR.z);
        if (markerRT != null) markerRT.position = new Vector3(pRT.x, pRT.y, pRT.z);

        // Log cada cierto tiempo (para README/captura)
        if (Time.frameCount % 30 == 0)
        {
            Debug.Log(
                $"p = {p}\n" +
                $"(T*R)*p = {pTR}  -> Marker_TR\n" +
                $"(R*T)*p = {pRT}  -> Marker_RT\n" +
                $"Equal? {ApproximatelyEqual(pTR, pRT)}"
            );
        }
    }

    private bool ApproximatelyEqual(Vector4 a, Vector4 b, float eps = 1e-4f)
    {
        return Mathf.Abs(a.x - b.x) < eps &&
               Mathf.Abs(a.y - b.y) < eps &&
               Mathf.Abs(a.z - b.z) < eps &&
               Mathf.Abs(a.w - b.w) < eps;
    }
}