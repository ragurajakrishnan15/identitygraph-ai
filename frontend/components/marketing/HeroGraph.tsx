"use client";
import { motion, useReducedMotion } from "framer-motion";

// A fixed, illustrative identity ring: one device shared by several "applicants".
const CENTER = { x: 260, y: 210 };
const RING = Array.from({ length: 7 }, (_, i) => {
  const a = (Math.PI * 2 * i) / 7 - Math.PI / 2;
  return { x: CENTER.x + Math.cos(a) * 125, y: CENTER.y + Math.sin(a) * 125 };
});
const OUTER = [
  { x: 60, y: 90, to: 5 }, { x: 440, y: 70, to: 1 }, { x: 470, y: 330, to: 3 }, { x: 70, y: 340, to: 4 }, { x: 250, y: 20, to: 0 },
];
const CENTERED = { transformBox: "fill-box", transformOrigin: "center" } as const;

export function HeroGraph() {
  const reduce = useReducedMotion();
  const draw = (delay: number) => reduce ? {} : {
    initial: { pathLength: 0, opacity: 0 }, animate: { pathLength: 1, opacity: 1 }, transition: { duration: 1.1, delay, ease: "easeOut" as const },
  };
  const pop = (delay: number) => reduce ? {} : {
    initial: { scale: 0, opacity: 0 }, animate: { scale: 1, opacity: 1 }, transition: { type: "spring" as const, stiffness: 260, damping: 18, delay },
  };
  return (
    <svg viewBox="0 0 520 420" className="h-auto w-full" role="img" aria-label="Illustration: several applications linked to one shared device, flagged as a possible fraud ring">
      <defs>
        <radialGradient id="glow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#ff3b30" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#ff3b30" stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle cx={CENTER.x} cy={CENTER.y} r="170" fill="url(#glow)" />
      {OUTER.map((o, i) => (
        <motion.line key={`o${i}`} x1={o.x} y1={o.y} x2={RING[o.to].x} y2={RING[o.to].y} stroke="rgb(var(--line))" strokeWidth="1.5" {...draw(0.6 + i * 0.1)} />
      ))}
      {RING.map((p, i) => (
        <motion.line key={`r${i}`} x1={CENTER.x} y1={CENTER.y} x2={p.x} y2={p.y} stroke="#ff3b30" strokeOpacity="0.55" strokeWidth="1.8" {...draw(0.2 + i * 0.08)} />
      ))}
      {OUTER.map((o, i) => (
        <motion.circle key={`on${i}`} cx={o.x} cy={o.y} r="10" fill="rgb(var(--surface))" stroke="#8e8e93" strokeWidth="2" style={CENTERED} {...pop(1 + i * 0.08)} />
      ))}
      {RING.map((p, i) => (
        <motion.circle key={`rn${i}`} cx={p.x} cy={p.y} r="14" fill="rgb(var(--surface))" stroke="#0a84ff" strokeWidth="2.5" style={CENTERED} {...pop(0.5 + i * 0.08)} />
      ))}
      <motion.g style={CENTERED} {...pop(0.1)}>
        <circle cx={CENTER.x} cy={CENTER.y} r="30" fill="#ff3b30" />
        <text x={CENTER.x} y={CENTER.y + 4} textAnchor="middle" fontSize="11" fontWeight="600" fill="#fff">device</text>
      </motion.g>
      {!reduce && (
        <circle className="pulse-ring" cx={CENTER.x} cy={CENTER.y} r="30" fill="none" stroke="#ff3b30" strokeWidth="2" />
      )}
    </svg>
  );
}
