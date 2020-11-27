using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class PlayerUIManager: MonoBehaviour
{
    public Slider hpSlider;

   
    public void UpdateHP(int hp)
    {
        hpSlider.value = hp;
    }
}
