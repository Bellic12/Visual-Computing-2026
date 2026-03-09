using UnityEngine;

[RequireComponent(typeof(MeshFilter))]
public class NormalVisualizer : MonoBehaviour
{
    [Header("Visualización")]
    public float normalLength = 0.3f;
    public Color normalColor = Color.yellow;
    public bool showNormals = true;

    [Header("Shading")]
    public bool applyFlatShading = false;

    // Guardar datos originales como arrays separados
    private Vector3[] originalVertices;
    private int[]     originalTriangles;
    private Vector3[] originalNormals;

    private Mesh workingMesh;
    private bool currentState = false; // para detectar cambios

    void Start()
    {
        // Crear copia editable del mesh
        workingMesh = Instantiate(GetComponent<MeshFilter>().sharedMesh);
        GetComponent<MeshFilter>().mesh = workingMesh;

        // Guardar datos originales en arrays independientes
        originalVertices  = workingMesh.vertices;
        originalTriangles = workingMesh.triangles;
        originalNormals   = workingMesh.normals;

        Debug.Log($"✓ Mesh listo. Vértices: {originalVertices.Length}");
    }

    void Update()
    {
        // Solo actuar cuando cambia el checkbox
        if (applyFlatShading == currentState) return;
        currentState = applyFlatShading;

        if (applyFlatShading)
        {
            ApplyFlat();
            Debug.Log("► Flat shading aplicado");
        }
        else
        {
            ApplySmooth();
            Debug.Log("► Smooth shading restaurado");
        }
    }

    void ApplySmooth()
    {
        // Restaurar desde los arrays originales guardados
        workingMesh.Clear();
        workingMesh.vertices  = originalVertices;
        workingMesh.triangles = originalTriangles;
        workingMesh.normals   = originalNormals;
        workingMesh.RecalculateNormals();
    }

    void ApplyFlat()
    {
        Vector3[] newVerts = new Vector3[originalTriangles.Length];
        int[]     newTris  = new int[originalTriangles.Length];

        for (int i = 0; i < originalTriangles.Length; i++)
        {
            newVerts[i] = originalVertices[originalTriangles[i]];
            newTris[i]  = i;
        }

        workingMesh.Clear();
        workingMesh.vertices  = newVerts;
        workingMesh.triangles = newTris;
        workingMesh.RecalculateNormals();
    }

    void OnDrawGizmos()
    {
        if (!showNormals) return;

        MeshFilter mf = GetComponent<MeshFilter>();
        if (mf == null || mf.sharedMesh == null) return;

        Mesh m             = mf.sharedMesh;
        Vector3[] vertices = m.vertices;
        Vector3[] normals  = m.normals;

        Gizmos.color = normalColor;

        for (int i = 0; i < vertices.Length; i++)
        {
            Vector3 worldPos    = transform.TransformPoint(vertices[i]);
            Vector3 worldNormal = transform.TransformDirection(normals[i]);
            Gizmos.DrawLine(worldPos, worldPos + worldNormal * normalLength);
        }
    }
}