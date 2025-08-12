import React from 'react'
import type { SignalItem } from '../api'

const fmtDate = (iso: string) =>
  new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false, // 24-hour format
  }).format(new Date(iso))

export default function SignalList({ rows, showChannel = false }: { rows: SignalItem[]; showChannel?: boolean }) {
  if (!rows.length) return <div className="p-3 text-sm text-neutral-600">No signals.</div>
  return (
    <div className="p-3 space-y-3">
      {rows.map(s => {
        const isLong = s.side === 'long'
        const sideColor = isLong ? 'text-green-600' : 'text-red-600'
        const dotColor = isLong ? 'bg-green-500' : 'bg-red-500'
        const channelLabel = s.channel_title || (s.channel_username ? `@${s.channel_username}` : null)

        return (
          <article key={s.id} className="border rounded p-3 bg-white">
            <header className="flex items-center justify-between text-sm">
              <div className="font-semibold flex items-center gap-2">
                <span>{s.symbol}</span>
                <span className={`inline-flex items-center gap-1 ${sideColor}`}>
                  <span className={`inline-block w-2 h-2 rounded-full ${dotColor}`} />
                  {s.side.toUpperCase()}
                </span>
              </div>
              <div className="text-neutral-500" title={s.message_date}>{fmtDate(s.message_date)}</div>
            </header>

            {showChannel && channelLabel && (
              <div className="mt-1 text-xs text-neutral-600">
                From: {channelLabel}
              </div>
            )}

            <div className="mt-2 text-sm">
              <div>TP: {s.take_profits.join(', ')}</div>
              {s.stop_loss && <div>SL: {s.stop_loss.join(', ')}</div>}
              {typeof s.leverage === 'number' && <div>Leverage: {s.leverage}x</div>}
            </div>
            <details className="mt-2">
              <summary className="cursor-pointer text-xs text-neutral-600">Original</summary>
              <pre className="whitespace-pre-wrap text-xs bg-neutral-50 p-2 rounded">{s.original_text}</pre>
            </details>
          </article>
        )
      })}
    </div>
  )
}
