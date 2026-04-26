import { Html } from "@react-three/drei";

export default function HtmlButtons({ playAction, names }) {
  return (
    <Html position={[0, 2, 0]}>
      <div style={{ display: "flex", gap: "10px" }}>
        {names.map((name) => (
          <button key={name} onClick={() => playAction(name)}>
            {name}
          </button>
        ))}
      </div>
    </Html>
  );
}