const vertexShader = `
varying vec3 vNormal;
varying vec3 vPosition;

void main() {
    vNormal = normalize(mat3(modelMatrix) * normal);
    vPosition = (modelMatrix * vec4(position, 1.0)).xyz;

    gl_Position = projectionMatrix * viewMatrix * vec4(vPosition, 1.0);
}
`;

const fragmentShader = `
uniform vec3 lightPosition;
uniform vec3 viewPosition;

uniform vec3 color;
uniform float shininess;

varying vec3 vNormal;
varying vec3 vPosition;

void main() {
    vec3 N = normalize(vNormal);
    vec3 L = normalize(lightPosition - vPosition);
    vec3 V = normalize(viewPosition - vPosition);

    // Diffuse
    float diff = max(dot(N, L), 0.0);

    // Reflect
    vec3 R = reflect(-L, N);

    // Specular
    float spec = pow(max(dot(R, V), 0.0), shininess);

    vec3 finalColor = color * diff + vec3(1.0) * spec;

    gl_FragColor = vec4(finalColor, 1.0);
}
`;

export {vertexShader, fragmentShader}