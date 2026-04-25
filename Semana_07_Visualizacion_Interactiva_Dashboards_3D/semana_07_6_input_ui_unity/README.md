# Taller - Entrada del Usuario e Interfaz UI en Unity y Three.js
## Nombre: 

- Juan David Buitrago Salazar
- Juan David Cardenas Galvis
- Nicolás Rodríguez Piraban
- Camilo Andres Medina Sanchez
- Juan Felipe Fajardo Garzón

## Fecha de entrega: 25/04/2026

## Descripción breve:
Este taller implementó un sistema de control de personaje en Unity con entrada de teclado y mouse, sistema de stamina con interfaz gráfica, y animaciones de ataque. El objetivo fue combinar inputs del usuario con UI reactiva para crear una experiencia de juego básica.

## Implementaciones:

### Unity:
Se implementó un CharacterController con movimiento WASD y rotación hacia la dirección de la cámara (Cinemachine Freelook camera). Se añadió un sistema de stamina que se consume al atacar (20 unidades por puño, 40 por patada) y se regenera automáticamente. La interfaz gráfica incluye una barra de stamina que refleja el porcentaje actual y un texto de estado que cambia según el nivel de energía (Enérgico/Cansado/Muy Cansado/Exhausto). Los ataques se activan con clicks del mouse (izquierdo para puño, derecho para patada) y disparan triggers de animación.

Adicionalmente se tiene un boton en la interfáz que activa una animación de victoria en el personaje

## Resultados visuales:

La escena muestra un personaje controlado que se mueve con WASD y la cámara con el movimiento del mouse, además de esto posee una animación de idle y caminata en posición de pelea.

![alt text](media/walking.gif)

La interfaz de usuario presenta una barra de stamina que se va vaciando al atacar y un texto que indica el estado actual del jugador. Al hacer click izquierdo el personaje ejecuta una animación de puño, y con click derecho una patada. Mientras el personaje no posea la cantidad de stamina necesaria no podrá efectuar un ataque (se puede evidenciar con los clicks efectuados en este momento)

![alt text](media/attack.gif)

Finalmente al presionar el botón de celebrar, el personaje va a efectuar una animación de victoria

![alt text](media/celeb.gif)

## Código relevante:
El script principal maneja el input, movimiento y sistema de stamina. Se usa `Input.GetAxis` para el desplazamiento del personaje e `Input.GetMouseButtonDown` para los ataques. La UI se actualiza modificando el `fillAmount` de la barra y el `text` del componente TMP_Text:

```csharp
float moverHorizontal = Input.GetAxis("Horizontal");
float moverVertical = Input.GetAxis("Vertical");

if (moverHorizontal != 0 || moverVertical != 0)
{
    transform.rotation = Quaternion.Euler(0, camara.eulerAngles.y, 0);
}
Vector3 movimiento = transform.right * moverHorizontal + transform.forward * moverVertical;
controller.Move(movimiento * velocidad * Time.deltaTime);
```

Los ataques reducen la estamina actual según el tipo y activan un trigger de animación en el AnimatorController
```csharp
if (Input.GetMouseButtonDown(0) && staminaActual >= 20f)
{
    animator.SetTrigger("Punch");
    staminaActual -= 20f;
}

if (Input.GetMouseButtonDown(1) && staminaActual >= 40f)
{
    animator.SetTrigger("Kick");
    staminaActual -= 40f;
}
```

Actualización de UI según el estado de stamina:
```csharp
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
```

Finalmente, las funciones encargadas de regenerar la stamina y de activar la celebración
```csharp
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
```

## Prompts utilizados:
No se hizo uso de IA generativa

## Aprendizajes y dificultades:
Este taller fue esencial para entender cómo conectar inputs del usuario con sistemas de juego y UI en Unity. Se aprendió a usar CharacterController para movement, TextMesh Pro para UI, y cómo actualizar elementos de UI desde código en tiempo real. La dificultad principal fue sincronizar las animaciones con los triggers de animator y asegurar que el sistema de stamina funcionara correctamente con la regeneración continua.