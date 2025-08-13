import React, { useState } from 'react'
import type { SignalItem, EditionItem } from '../api'
import { api } from '../api'

const fmtDate = (iso: string) =>
  new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(new Date(iso))

type RowProps = { s: SignalItem; showChannel: boolean; onDeleted: (id: number) => void }

function Row({ s, showChannel, onDeleted }: RowProps) {
  const [editions, setEditions] = useState<EditionItem[] | null>(null)
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  const loadEditions = async () => {
    setLoading(true)
    try {
      const data = await api.signalEditions(s.id)
      setEditions(data)
      setOpen(true)
    } finally { setLoading(false) }
  }

  const deleteMe = async () => {
    if (!confirm('Delete this signal? This cannot be undone.')) return
    await api.deleteSignal(s.id)
    onDeleted(s.id)
  }

  const isLong = s.side === 'long'
  const sideColor = isLong ? 'text-green-600' : 'text-red-600'
  const dotColor = isLong ? 'bg-green-500' : 'bg-red-500'
  const channelLabel = s.channel_title || (s.channel_username ? `@${s.channel_username}` : null)

  return (
    <article className="border rounded p-3 bg-white">
      <header className="flex items-center justify-between text-sm">
        <div className="font-semibold flex items-center gap-2">
          <span>{s.symbol}</span>
          <span className={`inline-flex items-center gap-1 ${sideColor}`}>
            <span className={`inline-block w-2 h-2 rounded-full ${dotColor}`} />
            {s.side.toUpperCase()}
          </span>
          {s.deleted && (
            <span className="ml-2 text-xs px-2 py-0.5 rounded bg-neutral-200 text-red-700">
              ⚠️ ✖️ DELETED
            </span>
          )}
          {s.edited && (
            <span className="ml-2 text-xs px-2 py-0.5 rounded bg-neutral-200 text-blue-700">
              ⚠️ ✏️ EDITED
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div className="text-neutral-500" title={s.message_date}>{fmtDate(s.message_date)}</div>
          <button
            title="Delete signal"
            onClick={deleteMe}
            className="px-2 py-1 text-neutral-500 hover:text-red-600"
            aria-label="Delete signal"
          >
            ✖
          </button>
        </div>
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

      {s.edited && (
        <div className="mt-2">
          {!open ? (
            <button
              onClick={loadEditions}
              disabled={loading}
              className="text-xs px-2 py-1 rounded border bg-neutral-50 hover:bg-neutral-100"
            >
              {loading ? 'Loading…' : 'Show edits'}
            </button>
          ) : (
            <div className="text-xs">
              <div className="font-semibold mb-1">Edit history</div>
              {editions?.length ? (
                <ul className="space-y-2">
                  {editions.map((e, idx) => (
                    <li key={idx} className="border rounded p-2 bg-neutral-50">
                      <div className="text-neutral-600 mb-1">{fmtDate(e.edited_at)}</div>
                      <pre className="whitespace-pre-wrap">{e.text}</pre>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-neutral-600">No editions available.</div>
              )}
            </div>
          )}
        </div>
      )}
    </article>
  )
}

export default function SignalList({ rows, showChannel = false }: { rows: SignalItem[]; showChannel?: boolean }) {
  const [list, setList] = useState(rows)
  React.useEffect(() => setList(rows), [rows])

  const onDeleted = (id: number) => {
    setList(prev => prev.filter(x => x.id !== id))
  }

  if (!list.length) return <div className="p-3 text-sm text-neutral-600">No signals.</div>
  return (
    <div className="p-3 space-y-3">
      {list.map(s => <Row key={s.id} s={s} showChannel={showChannel} onDeleted={onDeleted} />)}
    </div>
  )
}
