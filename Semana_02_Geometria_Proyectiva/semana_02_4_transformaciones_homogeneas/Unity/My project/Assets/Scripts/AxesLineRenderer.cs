using UnityEngine;

public class AxesLineRenderer : MonoBehaviour
{
    public float axisLength = 1.0f;
    private LineRenderer xLine, yLine, zLine;

    void Awake()
    {
        xLine = CreateLine("X_Axis");
        yLine = CreateLine("Y_Axis");
        zLine = CreateLine("Z_Axis");

        xLine.startColor = xLine.endColor = Color.red;
        yLine.startColor = yLine.endColor = Color.green;
        zLine.startColor = zLine.endColor = Color.blue;
    }

    LineRenderer CreateLine(string name)
    {
        GameObject go = new GameObject(name);
        go.transform.SetParent(transform, false);

        var lr = go.AddComponent<LineRenderer>();
        lr.positionCount = 2;
        lr.startWidth = 0.03f;
        lr.endWidth = 0.03f;
        lr.useWorldSpace = true;  // posiciones en mundo
        lr.material = new Material(Shader.Find("Sprites/Default"));
        return lr;
    }

    void Update()
    {
        Vector3 o = transform.position;
        xLine.SetPosition(0, o);
        xLine.SetPosition(1, o + transform.right * axisLength);

        yLine.SetPosition(0, o);
        yLine.SetPosition(1, o + transform.up * axisLength);

        zLine.SetPosition(0, o);
        zLine.SetPosition(1, o + transform.forward * axisLength);
    }
}