using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerManager : MonoBehaviour
{
    float straightSpeed = 24.0f;
    float rotationSpeed = 2.0f;

    float straight;
    float rotation;

    Rigidbody rb;
    Animator animator;


    void Start()
    {
        rb = GetComponent<Rigidbody>();
        animator = GetComponent<Animator>();
    }

    void Update()
    {
        //移動入力
        straight = Input.GetAxisRaw("Vertical");
        rotation = Input.GetAxisRaw("Horizontal");

        //攻撃入力
        if(Input.GetKeyDown(KeyCode.Space))
        {
            Debug.Log("攻撃");
            animator.SetTrigger("Attack");
        }
    }

    private void FixedUpdate()
    {
        rb.velocity = rb.transform.forward * straight * straightSpeed;
        rb.angularVelocity = new Vector3(0, rotation, 0) * rotationSpeed;
        animator.SetFloat("Speed", rb.velocity.magnitude);
    }
}
