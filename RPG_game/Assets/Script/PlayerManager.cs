using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System;
using System.Text;

public class PlayerManager : MonoBehaviour
{
    float straightSpeed = 24.0f;
    float rotationSpeed = 2.0f;

    float straight;
    float rotation;

    int maxHp = 100;
    int hp;

    Rigidbody rb;
    Animator animator;

    string input;

    bool debugMode = true;


    void Start()
    {
        hp = maxHp;
        rb = GetComponent<Rigidbody>();
        animator = GetComponent<Animator>();
        input = "";
    }

    void Update()
    {
        if (debugMode) // デバッグ時
        {
            //移動入力
            straight = Input.GetAxisRaw("Vertical");
            rotation = Input.GetAxisRaw("Horizontal");

            //攻撃入力
            if (Input.GetKeyDown(KeyCode.Space))
            {
                Debug.Log("攻撃");
                animator.SetTrigger("Attack");
            }
        }
        else // 本番時
        {
            input = "";

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
        Debug.Log("Arthur HP:" + hp);
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
