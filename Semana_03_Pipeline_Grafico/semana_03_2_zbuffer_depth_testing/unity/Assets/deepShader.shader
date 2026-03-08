Shader "Custom/DeepShader_Comparison"
{
    Properties
    {
        [MainColor] _BaseColor("Base Color", Color) = (1, 1, 1, 1)
        [Toggle] _UseLinear("Usar Profundidad Lineal", Float) = 0
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

            struct Attributes {
                float4 positionOS : POSITION;
            };

            struct Varyings {
                float4 positionCS : SV_POSITION;
            };

            CBUFFER_START(UnityPerMaterial)
                float _UseLinear;
            CBUFFER_END

            Varyings vert(Attributes IN) {
                Varyings OUT;
                OUT.positionCS = TransformObjectToHClip(IN.positionOS.xyz);
                return OUT;
            }

            half4 frag(Varyings IN) : SV_Target {
                float depth;

                if (_UseLinear > 0.5) {
                    // MODO LINEAL: Distancia real / Far Plane
                    depth = IN.positionCS.w / _ProjectionParams.z;
                }
                else {
                    depth = UNITY_Z_0_FAR_FROM_CLIPSPACE(IN.positionCS.z);
                }

                return float4(depth, depth, depth, 1.0);
            }
            ENDHLSL
        }
    }
}