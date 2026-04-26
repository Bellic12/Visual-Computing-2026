import { useRef, useEffect, useState } from "react";
import { useGLTF, useAnimations } from "@react-three/drei";
import HtmlButtons from "./HtmlButtons";

export default function Character() {
  const group = useRef();

  const { scene, animations } = useGLTF("/models/character.glb");
  console.log(animations);
  const { actions, names } = useAnimations(animations, group);

  const [currentAction, setCurrentAction] = useState(null);

  const playAction = (name) => {
    if (!actions[name]) return;

    if (currentAction && actions[currentAction]) {
      actions[currentAction].fadeOut(0.3);
    }

    actions[name].reset().fadeIn(0.3).play();
    setCurrentAction(name);
  };

  // Teclado
  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "r") playAction("Run");
      if (e.key === "j") playAction("Jump");
    };

    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [currentAction, actions]);

  return (
    <group
      ref={group}
      onClick={() => playAction("Wave")}
      onPointerOver={() => playAction("Idle")}
    >
      <primitive object={scene} scale={1.5} />
      <HtmlButtons playAction={playAction} names={names} />
    </group>
  );
}