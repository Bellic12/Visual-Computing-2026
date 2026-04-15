using UnityEngine;
using UnityEngine.AI;


public enum AIState { Idle, Patrol, Chase }

public class Zombie_patrol : MonoBehaviour
{
    public float detectionRadius = 5f;
    public float loseRadius = 7f;
    public Transform player; // Referencia al jugador

    public Transform[] waypoints; // Array de puntos de patrulla
    private NavMeshAgent agent;
    private int currentWaypointIndex = 0;

    private Animator animator;

    private AIState currentState = AIState.Idle;

    private float idleTimer = 0f;

    void Start() {
        agent = GetComponent<NavMeshAgent>();
        animator = GetComponent<Animator>();
        currentState = AIState.Idle; // Empezar patrullando
    }

    void Update() {
        switch (currentState) {
            case AIState.Idle:
                HandleIdleState();
                break;
            case AIState.Patrol:
                HandlePatrolState();
                break;
            case AIState.Chase:
                HandleChaseState();
                break;
        }

        float currentSpeed = agent.velocity.magnitude;
        animator.SetFloat("Speed", currentSpeed);

    }

    void HandleIdleState() {
        agent.speed = 0f; // Detenerse
        idleTimer += Time.deltaTime;
        if (idleTimer >= 2f) {
            currentState = AIState.Patrol;
            idleTimer = 0f;
        }
    }

    void HandleChaseState() {
        agent.SetDestination(player.position);
        agent.speed = 2f; // Corre más rápido
        if (PlayerDistance() > loseRadius) {
            currentState = AIState.Patrol;
        }
    }

    void HandlePatrolState() {
        // Si llega al punto de patrulla, va al siguiente
        if (!agent.pathPending && agent.remainingDistance < 0.5f) {
            currentWaypointIndex = (currentWaypointIndex + 1) % waypoints.Length;
            if (waypoints.Length > 0) {
                agent.SetDestination(waypoints[currentWaypointIndex].position);
                agent.speed = 0.5f; // Camina lento
            }
        }
        if (PlayerDistance() < detectionRadius) {
            currentState = AIState.Chase;
        }
    }

    float PlayerDistance(){
        return Vector3.Distance(transform.position, player.position);
    } 

}
