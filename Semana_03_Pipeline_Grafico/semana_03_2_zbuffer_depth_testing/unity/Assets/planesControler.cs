using UnityEngine;
using UnityEngine.UI;

public class planesControler : MonoBehaviour
{
    [Header("Camera")]
    public Camera cam;

    [Header("Far plane Slider")]

    public Slider farSlider;
    
    [Header("Near plane Slider")]

    public Slider nearSlider;

    public float far;
    public float near;

    void Start()
    {
        
    }

    void Update()
    {
        far = farSlider.value;
        near = nearSlider.value;
        cam.nearClipPlane = near;
        cam.farClipPlane = far;
    }
}
