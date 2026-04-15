using UnityEngine;

public class ColisionParticulas : MonoBehaviour
{
    public ParticleSystem efecto;

    private void OnCollisionEnter(Collision collision)
    {
        if (efecto != null)
        {
            efecto.transform.position = collision.contacts[0].point;
            efecto.Play();
        }
    }
}