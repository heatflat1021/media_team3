using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System;
using System.Text;
using UnityEngine.UI;

public class FileReader : MonoBehaviour
{
    public string guitxt = "";

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        ReadFile();
        this.GetComponentInChildren<Canvas>().GetComponentInChildren<Text>().text = guitxt;
    }

    void ReadFile()
    {
        // a.txtファイルを読み込む
        FileInfo fi = new FileInfo("./a.txt");
        try
        {
            // 一行毎読み込み
            using (StreamReader sr = new StreamReader(fi.OpenRead(), Encoding.UTF8))
            {
                guitxt = sr.ReadToEnd();
            }
        }
        catch (Exception e)
        {
            // 改行コード
            guitxt = SetDefaultText();
        }
    }

    // 改行コード処理
    string SetDefaultText()
    {
        return "No Input";
    }

}
