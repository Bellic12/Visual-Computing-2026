using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ControladorJerarquia : MonoBehaviour
{
    [Header("Objeto Padre")]
    public Transform padre;

    [Header("Sliders de Posición")]
    public Slider sliderPosX, sliderPosY, sliderPosZ;

    [Header("Sliders de Rotación")]
    public Slider sliderRotX, sliderRotY, sliderRotZ;

    [Header("Sliders de Escala")]
    public Slider sliderEscX, sliderEscY, sliderEscZ;

    [Header("UI Info")]
    public TMP_Text textInfo;

    [Header("Bonus - Animación")]
    public Button btnAnimar;
    public Button btnReiniciar;

    private bool animando;
    private Vector3    _posOrigen;
    private Quaternion _rotOrigen;
    private Vector3    _escOrigen;

    private const float VelocidadRotacion = 50f;

    // ─── Ciclo de vida ────────────────────────────────────────────────────────

    void Start()
    {
        GuardarEstadoInicial();
        btnAnimar.onClick.AddListener(ToggleAnimacion);
        btnReiniciar.onClick.AddListener(Reiniciar);
    }

    void Update()
    {
        if (animando) EjecutarAnimacion();
        else          AplicarSliders();

        ActualizarTexto();
    }

    // ─── Lógica principal ─────────────────────────────────────────────────────

    void AplicarSliders()
    {
        padre.position   = LeerVector3(sliderPosX, sliderPosY, sliderPosZ);
        padre.rotation   = Quaternion.Euler(LeerVector3(sliderRotX, sliderRotY, sliderRotZ));
        padre.localScale = LeerVector3(sliderEscX, sliderEscY, sliderEscZ);
    }

    void EjecutarAnimacion()
    {
        float delta = VelocidadRotacion * Time.deltaTime;
        padre.Rotate(delta, delta, delta);

        SincronizarSliderRotacion();
    }

    void SincronizarSliderRotacion()
    {
        Vector3 angulos = padre.eulerAngles;
        sliderRotX.value = angulos.x;
        sliderRotY.value = angulos.y;
        sliderRotZ.value = angulos.z;
    }

    void ActualizarTexto()
    {
        textInfo.text = $"Posición:  {padre.position}\n"
                      + $"Rotación:  {padre.eulerAngles}\n"
                      + $"Escala:    {padre.localScale}";
    }

    // ─── Botones ──────────────────────────────────────────────────────────────

    void ToggleAnimacion()
    {
        animando = !animando;
        SetTextoBoton(btnAnimar, animando ? "⏸ Pausar" : "▶ Animar");
    }

    void Reiniciar()
    {
        animando = false;
        RestaurarTransform();
        ResetearSliders();
        SetTextoBoton(btnAnimar, "▶ Animar");
    }

    // ─── Helpers ──────────────────────────────────────────────────────────────

    void GuardarEstadoInicial()
    {
        _posOrigen = padre.position;
        _rotOrigen = padre.rotation;
        _escOrigen = padre.localScale;
    }

    void RestaurarTransform()
    {
        padre.position   = _posOrigen;
        padre.rotation   = _rotOrigen;
        padre.localScale = _escOrigen;
    }

    void ResetearSliders()
    {
        sliderPosX.value = sliderPosY.value = sliderPosZ.value = 0f;
        sliderRotX.value = sliderRotY.value = sliderRotZ.value = 0f;
        sliderEscX.value = sliderEscY.value = sliderEscZ.value = 1f;
    }

    static Vector3 LeerVector3(Slider x, Slider y, Slider z)
        => new Vector3(x.value, y.value, z.value);

    static void SetTextoBoton(Button btn, string texto)
        => btn.GetComponentInChildren<TMP_Text>().text = texto;
}