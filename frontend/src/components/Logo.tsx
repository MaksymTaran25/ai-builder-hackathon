/** GovMatch mark: a compass rose drawn in the map's own hairlines, with the
 *  north point filled in cobalt — "the one direction worth taking". */
export default function Logo({ size = 22, wordmark = true }: { size?: number; wordmark?: boolean }) {
  return (
    <span className="inline-flex items-center gap-2.5">
      <svg
        className="mark"
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
      >
        <circle cx="12" cy="12" r="10.5" stroke="currentColor" strokeWidth="1" />
        {/* four hairline points */}
        <path d="M12 3.5 L13.6 10.4 L20.5 12 L13.6 13.6 L12 20.5 L10.4 13.6 L3.5 12 L10.4 10.4 Z" stroke="currentColor" strokeWidth="1" strokeLinejoin="round" />
        {/* north point, filled accent */}
        <path d="M12 3.5 L13.6 10.4 L12 12 L10.4 10.4 Z" fill="var(--accent)" />
        <circle cx="12" cy="12" r="1.2" fill="currentColor" />
      </svg>
      {wordmark && (
        <span className="text-[15px] font-medium tracking-tight text-ink">
          Gov<span className="text-graphite">Match</span>
        </span>
      )}
    </span>
  )
}
