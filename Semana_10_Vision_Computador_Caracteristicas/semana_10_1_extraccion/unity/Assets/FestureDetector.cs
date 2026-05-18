using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using OpenCVForUnity.CoreModule;
using OpenCVForUnity.Features2dModule;
using OpenCVForUnity.ImgprocModule;
using OpenCVForUnity.UnityIntegration;

public class FestureDetector : MonoBehaviour
{
    [Header("UI Elements")]
    [SerializeField] private RawImage displayImage;
    [SerializeField] private TMPro.TMP_Dropdown algorithmDropdown;

    [Header("Settings")]
    [SerializeField] private string resourceImageName = "bike";

    private Mat originalMat;
    private Mat outputMat;
    private Texture2D resultTexture;

    private enum AlgorithmType { ORB, SIFT }
    private AlgorithmType currentAlgorithm = AlgorithmType.ORB;

    void Start()
    {
        LoadImageFromResources();
        algorithmDropdown.onValueChanged.AddListener(OnAlgorithmChanged);
        ProcessImage();
    }

    void LoadImageFromResources()
    {
        Texture2D imgTexture = Resources.Load<Texture2D>(resourceImageName);
        if (imgTexture == null)
        {
            Debug.LogError($"No se encontró la imagen '{resourceImageName}' en la carpeta Resources.");
            return;
        }

        originalMat = new Mat(imgTexture.height, imgTexture.width, CvType.CV_8UC4);
        outputMat = new Mat(imgTexture.height, imgTexture.width, CvType.CV_8UC4);

        
        OpenCVMatUtils.Texture2DToMat(imgTexture, originalMat);
        
        resultTexture = new Texture2D(originalMat.cols(), originalMat.rows(), TextureFormat.RGBA32, false);
        displayImage.texture = resultTexture;
    }

    void ProcessImage()
    {
        if (originalMat == null) return;

        originalMat.copyTo(outputMat);
        MatOfKeyPoint keyPoints = new MatOfKeyPoint();

        if (currentAlgorithm == AlgorithmType.ORB)
        {
            ORB orb = ORB.create();
            orb.detect(originalMat, keyPoints);
            orb.Dispose();
        }
        else if (currentAlgorithm == AlgorithmType.SIFT)
        {
            SIFT sift = SIFT.create();
            sift.detect(originalMat, keyPoints);
            sift.Dispose();
        }

        
        Features2d.drawKeypoints(originalMat, keyPoints, outputMat, new Scalar(0, 255, 0, 255), 4);

        
        OpenCVMatUtils.MatToTexture2D(outputMat, resultTexture);

        keyPoints.Dispose();
    }

    void OnAlgorithmChanged(int index)
    {
        currentAlgorithm = (AlgorithmType)index;
        ProcessImage();
    }

    void OnDestroy()
    {
        if (originalMat != null) originalMat.Dispose();
        if (outputMat != null) outputMat.Dispose();
    }
}