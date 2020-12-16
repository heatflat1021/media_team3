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
    int cursor_change_counter = 0;

    public GameObject vanishmentParticle;
    public GameObject vanishmentParticle2;

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
        float calcuratedDistance = Mathf.Sqrt(Mathf.Pow(target.position.x - agent.transform.position.x, 2) + (Mathf.Pow(target.position.z - agent.transform.position.z, 2)));
        animator.SetFloat("Distance", calcuratedDistance);
        
        if(!is_red && calcuratedDistance < 65.0f && cursor_change_counter > 20) // カーソルを緑から赤へ
        {
            cursor.SetActive(false);
            cursor_red.SetActive(true);
            is_red = true;
            cursor_change_counter = 0;
            agent.velocity = new Vector3(0, 0, 0);
        }
        else if(is_red && calcuratedDistance > 63.0f && cursor_change_counter > 20) // カーソルを赤から緑へ
        {
            cursor.SetActive(true);
            cursor_red.SetActive(false);
            is_red = false;
            cursor_change_counter = 0;
        }
        cursor_change_counter++;
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
            Instantiate(vanishmentParticle, this.transform.position, Quaternion.identity);
            Instantiate(vanishmentParticle2, this.transform.position, Quaternion.identity);
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
