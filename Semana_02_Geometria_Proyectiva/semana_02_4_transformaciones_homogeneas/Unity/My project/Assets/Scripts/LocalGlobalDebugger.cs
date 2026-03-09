using UnityEngine;

public class LocalGlobalDebugger : MonoBehaviour
{
    [Header("References")]
    public Transform basePivot;      // BasePivot (vacío)
    public Transform armPivot;       // ArmPivot (vacío)
    public Transform endEffectorObj; // EndEffector (esfera)

    [Header("Motion (play mode)")]
    public float baseMoveSpeed = 1.0f;
    public float baseRotateSpeed = 30.0f;

    [Header("Arm Rotation Limit")]
    public float armMaxAngle = 90.0f;     // +90 / -90 = 180 total
    public float armOscSpeed = 1.0f;      // velocidad de oscilación

    private void Update()
    {
        // Mover BASE en el mundo (global)
        float move = Mathf.Sin(Time.time) * baseMoveSpeed * Time.deltaTime;
        basePivot.position += new Vector3(move, 0f, 0f);

        // Rotar BASE en el mundo (afecta a todo lo que cuelga)
        basePivot.Rotate(Vector3.up, baseRotateSpeed * Time.deltaTime, Space.World);

        // Rotación LIMITADA del brazo: oscila entre -armMaxAngle y +armMaxAngle
        float angle = Mathf.Sin(Time.time * armOscSpeed) * armMaxAngle;
        armPivot.localRotation = Quaternion.Euler(0f, 0f, angle); // eje Z (como bisagra)

        // Log cada 20 frames
        if (Time.frameCount % 20 == 0)
        {
            Debug.Log(
                $"BASE  local:{basePivot.localPosition:F3} world:{basePivot.position:F3}\n" +
                $"ARM_P local:{armPivot.localPosition:F3} world:{armPivot.position:F3}\n" +
                $"END   local:{endEffectorObj.localPosition:F3} world:{endEffectorObj.position:F3}"
            );
        }
    }
}