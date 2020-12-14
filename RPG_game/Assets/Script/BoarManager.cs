using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

public class BoarManager : MonoBehaviour
{
    public Transform target;
    NavMeshAgent agent;
    Animator animator;

    public EnemyUIManager enemyUIManager;

    public int maxHp = 100;
    int hp;

    public GameObject cursor;
    public GameObject cursor_red;
    bool is_red = false;

    void Start()
    {
        hp = maxHp;
        enemyUIManager.Init(this);

        animator = GetComponentInChildren<Animator>();
        agent = GetComponent<NavMeshAgent>();
        agent.destination = target.position;
    }

    void Update()
    {
        agent.destination = target.position;
        animator.SetFloat("Distance", agent.remainingDistance);
        
        if(!is_red && agent.remainingDistance < 65.0f) // カーソルを緑から赤へ
        {
            cursor.SetActive(false);
            cursor_red.SetActive(true);
            is_red = true;
        }
        else if(is_red && agent.remainingDistance > 65.0f) // カーソルを赤から緑へ
        {
            cursor.SetActive(true);
            cursor_red.SetActive(false);
            is_red = false;
        }
    }
    
    void Damage(int damage)
    {
        hp -= damage;
        if (hp <= 0)
        {
            hp = 0;
        }
        enemyUIManager.UpdateHP(hp);
        if(hp > 0)
        {
            Debug.Log("Boar HP:" + hp);
        }
        else if (hp == 0)
        {
            Debug.Log("Boarは死んだ");
        }
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
