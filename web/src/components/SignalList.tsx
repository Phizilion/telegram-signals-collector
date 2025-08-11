import React from 'react'
import type { SignalItem } from '../api'

export default function SignalList({ rows }: { rows: SignalItem[] }) {
  if (!rows.length) return <div className="p-3 text-sm text-neutral-600">No signals.</div>
  return (
    <div className="p-3 space-y-3">
      {rows.map(s => (
        <article key={s.id} className="border rounded p-3 bg-white">
          <header className="flex items-center justify-between text-sm">
            <div className="font-semibold">{s.symbol} · {s.side.toUpperCase()}</div>
            <div className="text-neutral-500">{new Date(s.message_date).toLocaleString()}</div>
          </header>
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
      ))}
    </div>
  )
}
