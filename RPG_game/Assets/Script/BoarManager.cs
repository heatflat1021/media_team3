using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

public class BoarManager : MonoBehaviour
{
    public Transform target;
    NavMeshAgent agent;
    Animator animator;

    void Start()
    {
        animator = GetComponentInChildren<Animator>();
        agent = GetComponent<NavMeshAgent>();
        agent.destination = target.position;
    }

    void Update()
    {
        agent.destination = target.position;
        animator.SetFloat("Distance", agent.remainingDistance);
    }

    private void OnTriggerEnter(Collider other)
    {
        Damager damager = other.GetComponent<Damager>();
        if(damager != null)
        {
            Debug.Log("敵はダメージを受ける");
        }
    }
}
