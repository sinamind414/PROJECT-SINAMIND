export default function DnaMotif({ className = '', size = 120 }: { className?: string; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" className={className} fill="none">
      <g className="dna-spin" style={{ transformOrigin: '60px 60px' }}>
        {Array.from({ length: 11 }).map((_, i) => {
          const t = i / 10;
          const y = 10 + t * 100;
          const phase = t * Math.PI * 2;
          const x1 = 60 + Math.sin(phase) * 34;
          const x2 = 60 - Math.sin(phase) * 34;
          return (
            <g key={i}>
              <line x1={x1} y1={y} x2={x2} y2={y} stroke="rgba(45,212,191,0.25)" strokeWidth="1.2" />
              <circle cx={x1} cy={y} r={3.4} fill="#2DD4BF" opacity={0.9} />
              <circle cx={x2} cy={y} r={3.4} fill="#F59E0B" opacity={0.9} />
            </g>
          );
        })}
        <path d="M60 10 C 26 30, 94 50, 60 70 C 26 90, 94 100, 60 110" stroke="#2DD4BF" strokeWidth="2" opacity="0.5" />
        <path d="M60 10 C 94 30, 26 50, 60 70 C 94 90, 26 100, 60 110" stroke="#F59E0B" strokeWidth="2" opacity="0.5" />
      </g>
    </svg>
  );
}
