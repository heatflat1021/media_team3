using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System;
using System.Text;
using UnityEngine.UI;

public class FileReader : MonoBehaviour
{
    public string text = "";

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        ReadFile();
        this.GetComponentInChildren<Canvas>().GetComponentInChildren<Text>().text = text;
    }

    void ReadFile()
    {
        text = "";

        // eeg.txtファイルを読み込む
        FileInfo eeg = new FileInfo("./eeg.txt");
        try
        {
            // 一行毎読み込み
            using (StreamReader sr = new StreamReader(eeg.OpenRead(), Encoding.UTF8))
            {
                text += sr.ReadToEnd();
            }
        }
        catch (Exception e)
        {
            text += SetDefaultText();
        }

        text += "\n";

        // mot.txtファイルを読み込む
        FileInfo mot = new FileInfo("./mot.txt");
        try
        {
            // 一行毎読み込み
            using (StreamReader sr = new StreamReader(mot.OpenRead(), Encoding.UTF8))
            {
                text += sr.ReadToEnd();
            }
        }
        catch (Exception e)
        {
            text += SetDefaultText();
        }
    }

    // 改行コード処理
    string SetDefaultText()
    {
        return "NoInput";
    }

}
