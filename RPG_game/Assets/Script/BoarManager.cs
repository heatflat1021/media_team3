using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

public class BoarManager : MonoBehaviour
{
    public Transform target;
    NavMeshAgent agent;
    Animator animator;

    int maxHp = 100;
    int hp;

    void Start()
    {
        hp = maxHp;
        animator = GetComponentInChildren<Animator>();
        agent = GetComponent<NavMeshAgent>();
        agent.destination = target.position;
    }

    void Update()
    {
        agent.destination = target.position;
        animator.SetFloat("Distance", agent.remainingDistance);
    }

    void Damage(int damage)
    {
        hp -= damage;
        if (hp <= 0)
        {
            hp = 0;
        }
        Debug.Log("Boar HP:" + hp);
    }

    private void OnTriggerEnter(Collider other)
    {
        Damager damager = other.GetComponent<Damager>();
        if (damager != null)
        {
            Debug.Log("敵はダメージを受ける");
            Damage(damager.damage);
        }
    }
}
