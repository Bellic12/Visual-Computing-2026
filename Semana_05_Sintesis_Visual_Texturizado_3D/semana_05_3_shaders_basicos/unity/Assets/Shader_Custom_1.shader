Shader "Custom/NewUnlitUniversalRenderPipelineShader"
{
    Properties
    {
        [MainColor] _BaseColor("Base Color", Color) = (1, 1, 1, 1)
        [MainTexture] _BaseMap("Base Map", 2D) = "white" {}
        _TopColor("Top Color", Color) = (1, 0, 0, 1)
        _BottomColor("Bottom Color", Color) = (0, 0, 1, 1)
        _WaveSpeed("Wave Speed", Range(0, 5)) = 1.0
        _WaveIntensity("Wave Intensity", Range(0, 0.5)) = 0.1
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }

        Pass
        {
            HLSLPROGRAM

            #pragma vertex vert
            #pragma fragment frag

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionHCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
            };

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                float4 _BaseMap_ST;
                half4 _TopColor;
                half4 _BottomColor;
                float _WaveSpeed;
                float _WaveIntensity;
            CBUFFER_END

            Varyings vert(Attributes IN)
            {
                Varyings OUT;
                OUT.positionHCS = TransformObjectToHClip(IN.positionOS.xyz);
                OUT.uv = TRANSFORM_TEX(IN.uv, _BaseMap);
                OUT.positionWS = TransformObjectToWorld(IN.positionOS.xyz);
                return OUT;
            }

            half4 frag(Varyings IN) : SV_Target
            {
                // Normalizar la posición Y entre 0 y 1
                float t = saturate(IN.positionWS.y);

                // Efecto de ondulación con el tiempo
                float wave = sin(_Time.y * _WaveSpeed + IN.positionWS.y * 2.0);
                float waveOffset = wave * _WaveIntensity;

                // Interpolación lineal entre color inferior y superior
                half4 gradientColor = lerp(_BottomColor, _TopColor, saturate(t + waveOffset));

                half4 color = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, IN.uv) * _BaseColor * gradientColor;
                return color;
            }
            ENDHLSL
        }
    }
}