using UnityEngine;
using UnityEngine.UI; 
using TMPro; 

public class PJ_Actions : MonoBehaviour
{

    public TMP_Text textoEstado;
    public Image barraStamina;
    public float staminaActual = 100f;
    public float staminaMaxima = 100f;
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
        if (moverHorizontal != 0 || moverVertical != 0)
        {
            transform.rotation = Quaternion.Euler(0, camara.eulerAngles.y, 0);
        }
        // Calcular la dirección basada en hacia dónde mira el jugador
        Vector3 movimiento = transform.right * moverHorizontal + transform.forward * moverVertical;

        // Mover al jugador
        controller.Move(movimiento * velocidad * Time.deltaTime);
        
        // Aplicar un poco de gravedad simple para que no flote
        if (!controller.isGrounded)
        {
            controller.Move(Vector3.down * 9.81f * Time.deltaTime);
        }

        // Atacar gasta stamina, por lo que se debe comprobar si el jugador tiene suficiente stamina antes de permitir el ataque

        if (Input.GetMouseButtonDown(0) && staminaActual >= 20f)
        {
            //Disparador de puño
            animator.SetTrigger("Punch");
            staminaActual -= 20f; // Reducir stamina en 20 unidades por cada ataque de puño
        }

        
        if (Input.GetMouseButtonDown(1) && staminaActual >= 40f)
        {
            //Disparador de Patada
            animator.SetTrigger("Kick");
            staminaActual -= 40f; // Reducir stamina en 40 unidades por cada ataque de patada
        }
        

        float inputMagnitude = new Vector2(moverHorizontal, moverVertical).magnitude;
        Debug.Log("Magnitud de entrada " + inputMagnitude);
        animator.SetFloat("Speed", inputMagnitude, 0.1f, Time.deltaTime);

        ActualizarInterfaz();
        RegenerarStamina();
    }

    void ActualizarInterfaz()
    {   
        // Actualizar la barra de stamina
        barraStamina.fillAmount = staminaActual / staminaMaxima;
        // Actualizar el texto del estado en función de la stamina actual
        if (staminaActual >= 80f)
        {
            textoEstado.text = "Enérgico";
        }
        else if (staminaActual >= 50f)
        {
            textoEstado.text = "Cansado";
        }
        else if (staminaActual >= 20f)
        {
            textoEstado.text = "Muy Cansado";
        }
        else
        {
            textoEstado.text = "Exhausto";
        }
    }

    void RegenerarStamina()
    {
        if (staminaActual < staminaMaxima)
            staminaActual += 5f * Time.deltaTime;
    }

    public void Celebrar()
    {
        animator.SetTrigger("Celeb");
        Debug.Log("Botón presionado");
    }
}
