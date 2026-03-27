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
uniform vec3 color;

varying vec3 vNormal;
varying vec3 vPosition;

void main() {
    vec3 N = normalize(vNormal);
    vec3 L = normalize(lightPosition - vPosition);

    float diffuse = max(dot(N, L), 0.0);

    vec3 finalColor = color * diffuse;

    gl_FragColor = vec4(finalColor, 1.0);
}
`;

export {vertexShader, fragmentShader}