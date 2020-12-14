using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class EnemyUIManager : MonoBehaviour
{

    public Slider hpSlider;
    
    public void Init(BoarManager boarManager)
    {
        hpSlider.maxValue = boarManager.maxHp;
        hpSlider.value = boarManager.maxHp;
    }

    public void UpdateHP(int hp)
    {
        hpSlider.value = hp;
    }
}
