using UnityEngine;

public class Player_movement : MonoBehaviour
{
    public float velocidad = 0.5f;
    private CharacterController controller;

    public Transform camara;

    private Animator animator;

    void Start()
    {
        controller = GetComponent<CharacterController>();
        animator = GetComponent<Animator>();
    }

    void Update()
    {
        // Obtener movimiento de las teclas WASD o flechas
        float moverHorizontal = Input.GetAxis("Horizontal");
        float moverVertical = Input.GetAxis("Vertical");

        // Rotar el personaje hacia la dirección de la cámara (solo en el eje Y)
        transform.rotation = Quaternion.Euler(0, camara.eulerAngles.y, 0);

        // Calcular la dirección basada en hacia dónde mira el jugador
        Vector3 movimiento = transform.right * moverHorizontal + transform.forward * moverVertical;

        // Mover al jugador
        controller.Move(movimiento * velocidad * Time.deltaTime);
        
        // Aplicar un poco de gravedad simple para que no flote
        if (!controller.isGrounded)
        {
            controller.Move(Vector3.down * 9.81f * Time.deltaTime);
        }

        float currentSpeed = controller.velocity.magnitude;
        Debug.Log("Velocidad del jugador: " + currentSpeed);
        animator.SetFloat("Speed", currentSpeed, 0.15f, Time.deltaTime);
    }
}
