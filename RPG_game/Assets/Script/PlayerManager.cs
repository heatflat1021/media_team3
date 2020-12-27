using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System;
using System.Text;

public class PlayerManager : MonoBehaviour
{
    public Transform target;
    public Transform player;
    
    float straightSpeed = 24.0f;
    float rotationSpeed = 2.0f;

    float straight;
    float rotation;

    public PlayerUIManager playerUIManager;

    public int maxHp = 100;
    int hp;

    Rigidbody rb;
    Animator animator;

    // 炎関連
    public GameObject fire;
    public bool fireFlag = false;
    public int fireCounter = 0;

    // 岩関連
    public GameObject rock1;
    public GameObject rock2;
    bool rockFlag = false;

    string input;

    bool debugMode = true;


    void Start()
    {
        hp = maxHp;
        playerUIManager.Init(this);
        rb = GetComponent<Rigidbody>();
        animator = GetComponent<Animator>();
        fire.SetActive(false); 
        input = "";
    }

    void Update()
    {//岩とplayerの距離
        var heading = target.position - player.position;
        var distance = heading.magnitude;

        //
        if (debugMode) // デバッグ時
        {
            //移動入力
            straight = Input.GetAxisRaw("Vertical");
            rotation = Input.GetAxisRaw("Horizontal");

            //攻撃入力
            if (Input.GetKeyDown(KeyCode.Space))
            {
                // Debug.Log("攻撃");
                // animator.SetTrigger("Attack");

                // 炎コマンドの起動
                if (!fireFlag)
                {
                    Debug.Log("炎");
                    animator.SetTrigger("Fire");
                    fireFlag = true;
                }

                // 岩のサイコキネシス
                if (distance < 50)
                {
                    rock1.transform.Translate(0, 0.2f - UnityEngine.Random.value, 0);
                    rock2.transform.Translate(0, -0.2f + UnityEngine.Random.value, 0);
                }
            }
        }
        else // 本番時
        {
            input = "";
            rockFlag = false;

            // eeg.txtファイルを読み込む
            FileInfo eeg = new FileInfo("./eeg.txt");
            try
            {
                // 一行毎読み込み
                using (StreamReader sr = new StreamReader(eeg.OpenRead(), Encoding.UTF8))
                {
                    input += sr.ReadToEnd();
                }
            }
            catch (Exception e)
            {
                input += SetDefaultText();
            }

            // TODO:  EEGデータから操作
            Debug.Log(input);
            if(input == "STRAIGHT")
            {
                straight = 1;
                straightSpeed = 24.0f;
            }
            else if(input == "NEUTRAL")
            {
                straight = 0;
                straightSpeed = 0;
            }
            else if(input == "SWORD")
            {
                Debug.Log("攻撃");
                animator.SetTrigger("Attack");
            }
            else if(input == "MAGIC1")
            {
                // 炎コマンドの起動
                if (!fireFlag)
                {
                    Debug.Log("炎");
                    animator.SetTrigger("Fire");
                    fireFlag = true;
                }
            }
            else if(input == "MAGIC2")
            {
                Debug.Log("MAGIC2");
                // 岩のサイコキネシス
                rock1.transform.Translate(0, 3.2f - UnityEngine.Random.value, 0);
                rock2.transform.Translate(0, -3.2f + UnityEngine.Random.value, 0);
                rockFlag = true;
            }

            input = "";

            // mot.txtファイルを読み込む
            FileInfo mot = new FileInfo("./mot.txt");
            try
            {
                // 一行毎読み込み
                using (StreamReader sr = new StreamReader(mot.OpenRead(), Encoding.UTF8))
                {
                    input += sr.ReadToEnd();
                }
            }
            catch (Exception e)
            {
                input += SetDefaultText();
            }

            // TODO: モーションデータから操作
            if(input == "STRAIGHT")
            {
                rotation = 0;
                rotationSpeed = 0;
            }
            else if(input == "RIGHT")
            {
                rotation = 1;
                rotationSpeed = 2.0f;
            }
            else if(input == "LEFT")
            {
                rotation = -1;
                rotationSpeed = 2.0f;
            }
        }

        // 炎コマンドの更新
        if (fireFlag)
        {
            fireCounter++;
            if(fireCounter == 70)
            {
                fire.SetActive(true);
            }
            if(fireCounter > 240)
            {
                fire.SetActive(false);
                fireCounter = 0;
                fireFlag = false;
            }
        }

        // 岩の重力落下
        if (!rockFlag)
        {
            if (rock1.transform.position.y > 4.3 && !rock1.GetComponent<RockManager>().reachedToEnemy)
            {
                rock1.transform.Translate(0, 0.01f, 0);
            }
            if (rock2.transform.position.y > 6.1)
            {
                rock2.transform.Translate(0, -0.03f, 0);
            }
        }
    }

    private void FixedUpdate()
    {
        rb.velocity = rb.transform.forward * straight * straightSpeed;
        rb.angularVelocity = new Vector3(0, rotation, 0) * rotationSpeed;
        animator.SetFloat("Speed", rb.velocity.magnitude);
    }

    string SetDefaultText()
    {
        return "NoInput";
    }

    //武器の判定を有効にしたり消したりする関数
    public void HideColliderWeapon()
    {

    }
    public void ShowColliderWeapon()
    {

    }


    void Damage(int damage)
    {
        hp -= damage;
        if (hp <= 0)
        {
            hp = 0;
        }
        playerUIManager.UpdateHP(hp);
        Debug.Log("Arthur HP:" + hp*160);
    }

    private void OnTriggerEnter(Collider other)
    {
        Damager damager = other.GetComponent<Damager>();
        if (damager != null)
        {
            Debug.Log("Playerはダメージを受ける");
            Damage(damager.damage);
        }
    }
}
