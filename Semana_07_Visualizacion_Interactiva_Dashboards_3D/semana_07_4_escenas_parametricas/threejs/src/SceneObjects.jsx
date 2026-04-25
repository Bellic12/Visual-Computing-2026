import { useRef, useEffect, useState } from "react";
import { useControls,button } from "leva";

const objectsData = [
  { id: 1, position: [0, 0, 0],  scale: 1,   color: "red",    type: "box" },
  { id: 2, position: [2, 0, 0],  scale: 0.8, color: "blue",   type: "sphere" },
  { id: 3, position: [-2, 0, 0], scale: 1.2, color: "green",  type: "box" },
  { id: 4, position: [0, 2, 0],  scale: 0.6, color: "orange", type: "sphere" },
];

export default function SceneObjects() {
  // 🔹 estado real de los objetos (editable)
  const [objects, setObjects] = useState(objectsData);
  // 🔹 selección múltiple
  const [selectedIds, setSelectedIds] = useState([]);
  // 🔹 ref
  const selectedIdsRef = useRef(selectedIds); 
  useEffect(() => {
    selectedIdsRef.current = selectedIds;
  }, [selectedIds]);

  // 🔹 controles con Leva
  const [controls, setControls] = useControls(() => ({
    scaleMultiplier: { value: 1, min: 0.2, max: 3 },
    positionOffset: {value: {x: 0, y: 0, z: 0}, step: 0.1},
    color: "#ff0000",
    wireframe: false,
    apply: button((get) => {
      const selected = selectedIdsRef.current;
      if (selected.length === 0) return;

      const conColor = get('color')
      const conScale = get('scaleMultiplier')
      const conOffst = get('positionOffset')

      setObjects((prev) =>
        prev.map((obj) =>
          selected.includes(obj.id)
            ? {
                ...obj,
                scale: obj.scale * conScale,
                color: conColor,
                position: [
                  obj.position[0] + conOffst.x,
                  obj.position[1] + conOffst.y,
                  obj.position[2] + conOffst.z,
                ],
              }
            : obj
        )
      );
      
      setSelectedIds([]);

      setControls({
        scaleMultiplier: 1,
        positionOffset: {x: 0, y: 0, z: 0},
        color: "#ff0000",
        wireframe: false,
      });
    }),
  }));

  return (
    <>
      {objects.map((obj) => {
        const isSelected = selectedIds.includes(obj.id);

        return (
          <mesh
            key={obj.id}
            position={isSelected ? [
                      obj.position[0] + controls.positionOffset.x,
                      obj.position[1] + controls.positionOffset.y,
                      obj.position[2] + controls.positionOffset.z,
                    ] : obj.position}
            scale={isSelected ? obj.scale * controls.scaleMultiplier : obj.scale}
            onClick={(e) => {
              e.stopPropagation(); // evita clicks raros en la escena

              setSelectedIds((prev) =>
                prev.includes(obj.id)
                  ? prev.filter((id) => id !== obj.id) // quitar selección
                  : [...prev, obj.id] // agregar selección
              );
            }}
          >
            {/* Geometría condicional */}
            {obj.type === "box" ? (
              <boxGeometry />
            ) : (
              <sphereGeometry />
            )}

            {/* Material */}
            <meshStandardMaterial
              color={isSelected ? controls.color : obj.color}
              wireframe={controls.wireframe && isSelected}
              emissive={isSelected ? "white" : "black"} // resalta seleccionados
              emissiveIntensity={isSelected ? 0.5 : 0}
            />
          </mesh>
        );
      })}
    </>
  );
}