using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraController : MonoBehaviour
{
    // プレイヤーアバターをInspectorで入れる
    [SerializeField] GameObject player;
    // Main CameraをInspectorで入れる
    [SerializeField] Camera cam;

    // カメラの相対位置を指定する変数
    float heightOffset = 12.0f;
    float backOffset = -20.0f;

    float rightWraparound = 0.0f;

    public GameObject enemy;

    void Update()
    {
        Vector3 playerPosition = player.transform.position;
        Vector3 playerAngle = player.transform.eulerAngles;
        Vector2 playerAngleVector = eularAngleToVector2(playerAngle.y);

        cam.transform.position = new Vector3(
            playerPosition.x + playerAngleVector.y * backOffset + playerAngleVector.x * rightWraparound,
            heightOffset,
            playerPosition.z + playerAngleVector.x * backOffset - playerAngleVector.y * rightWraparound);
        Quaternion rot = Quaternion.Euler(0, -rightWraparound, 0);
        cam.transform.rotation = player.transform.rotation * rot;

        if (enemy == null || !enemy.GetComponentInChildren<BoarManager>().is_red)
        {
            if(rightWraparound > 0.0f)
            {
                rightWraparound -= 1.0f;
            }
        }
        else
        {
            if(rightWraparound < 25.0f)
            {
                rightWraparound += 1.0f;
            }
        }

    }

    Vector2 eularAngleToVector2(float eularAngle)
    {
        float x = Mathf.Cos(eularAngle * Mathf.Deg2Rad);
        float y = Mathf.Sin(eularAngle * Mathf.Deg2Rad);
        return new Vector2(x, y);
    }
}