export default function NeuronMotif({ className = '', size = 180 }: { className?: string; size?: number }) {
  const nodes = [
    { x: 30, y: 40 }, { x: 90, y: 25 }, { x: 150, y: 55 },
    { x: 50, y: 95 }, { x: 110, y: 110 }, { x: 160, y: 140 },
    { x: 20, y: 150 }, { x: 80, y: 165 },
  ];
  const links = [[0,1],[1,2],[0,3],[1,4],[2,5],[3,4],[4,5],[3,6],[4,7],[6,7]];
  return (
    <svg width={size} height={size * 0.95} viewBox="0 0 180 175" className={className} fill="none">
      {links.map(([a,b], i) => (
        <line key={i} x1={nodes[a].x} y1={nodes[a].y} x2={nodes[b].x} y2={nodes[b].y} stroke="rgba(45,212,191,0.18)" strokeWidth="1" />
      ))}
      {nodes.map((n, i) => (
        <g key={i}>
          <circle cx={n.x} cy={n.y} r="8" fill="rgba(45,212,191,0.12)" />
          <circle cx={n.x} cy={n.y} r="3.5" fill={i % 3 === 0 ? '#F59E0B' : '#2DD4BF'} opacity="0.85" />
        </g>
      ))}
    </svg>
  );
}
