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

    void Start()
    {
        rb = GetComponent<Rigidbody>();
    }

    void Update()
    {
        straight = Input.GetAxisRaw("Vertical");
        rotation = Input.GetAxisRaw("Horizontal");
    }

    private void FixedUpdate()
    {
        rb.velocity = rb.transform.forward * straight * straightSpeed;
        rb.angularVelocity = new Vector3(0, rotation, 0) * rotationSpeed;
    }
}
