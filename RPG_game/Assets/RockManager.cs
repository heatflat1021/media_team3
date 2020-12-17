using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

public class RockManager : MonoBehaviour
{

    public Transform target;
    NavMeshAgent agent;
    Animator animator;

    public bool toEnemy;
    public bool reachedToEnemy;

    // Start is called before the first frame update
    void Start()
    {
        animator = GetComponentInChildren<Animator>();
        agent = GetComponent<NavMeshAgent>();

        toEnemy = false;
        reachedToEnemy = false;
        agent.destination = target.position;
        agent.enabled = false;
    }

    // Update is called once per frame
    void Update()
    {
        if(agent.transform.position.y > 10)
        {
            toEnemy = true;
            agent.enabled = true;
        }

        if (toEnemy)
        {
            agent.destination = target.position;
            float calcuratedDistance = Mathf.Sqrt(Mathf.Pow(target.position.x - agent.transform.position.x, 2) + (Mathf.Pow(target.position.z - agent.transform.position.z, 2)));

            if (calcuratedDistance < 14.0f)
            {
                agent.velocity = new Vector3(0, 0, 0);
                reachedToEnemy = true;
            }
        }
    }
}
