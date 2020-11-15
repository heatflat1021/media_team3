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

    void Update()
    {
        Vector3 playerPosition = player.transform.position;
        Vector3 playerAngle = player.transform.eulerAngles;
        Vector2 playerAngleVector = eularAngleToVector2(playerAngle.y);

        cam.transform.position = new Vector3(
            playerPosition.x + playerAngleVector.y * backOffset,
            heightOffset,
            playerPosition.z + playerAngleVector.x * backOffset);
        cam.transform.rotation = player.transform.rotation;
    }

    Vector2 eularAngleToVector2(float eularAngle)
    {
        float x = Mathf.Cos(eularAngle * Mathf.Deg2Rad);
        float y = Mathf.Sin(eularAngle * Mathf.Deg2Rad);
        return new Vector2(x, y);
    }
}