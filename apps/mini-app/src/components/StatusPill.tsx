type StatusPillProps = {
  label: string;
  tone: "ready" | "pending";
};

export function StatusPill({ label, tone }: StatusPillProps) {
  return <span className={`status-pill status-pill--${tone}`}>{label}</span>;
}
