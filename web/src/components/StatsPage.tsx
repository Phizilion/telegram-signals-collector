import React, { useEffect, useState } from 'react'
import { api, ChannelStats, SymbolStats } from '../api'

type Props = { mode: 'channels' | 'symbols' }

export default function StatsPage({ mode }: Props) {
  const [rows, setRows] = useState<(ChannelStats | SymbolStats)[]>([])
  const [loading, setLoading] = useState(false)
  const load = async () => {
    setLoading(true)
    try {
      setRows(mode === 'channels' ? await api.channelStats() : await api.symbolStats())
    } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [mode])

  return (
    <div className="p-3">
      <div className="flex items-center justify-between mb-2">
        <h2 className="font-semibold">Statistics · {mode}</h2>
      </div>
      {loading && <div className="text-sm text-neutral-600 mb-2">Loading…</div>}
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm bg-white border">
          <thead className="bg-neutral-50">
            <tr>
              <th className="px-2 py-1 text-left">{mode==='channels' ? 'Channel' : 'Symbol'}</th>
              <th className="px-2 py-1 text-right">Total</th>
              <th className="px-2 py-1 text-right">Long</th>
              <th className="px-2 py-1 text-right">Short</th>
              <th className="px-2 py-1 text-right">Long/Total</th>
              <th className="px-2 py-1 text-right">Mean Lev</th>
              <th className="px-2 py-1 text-right">/Day</th>
              <th className="px-2 py-1 text-right">/Week</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, idx) => (
              <tr key={idx} className="border-t">
                <td className="px-2 py-1">
                  {'symbol' in r ? r.symbol : (r.title || r.username || r.channel_id)}
                </td>
                <td className="px-2 py-1 text-right">{r.total}</td>
                <td className="px-2 py-1 text-right">{r.long_count}</td>
                <td className="px-2 py-1 text-right">{r.short_count}</td>
                <td className="px-2 py-1 text-right">{r.long_total_ratio?.toFixed(3) ?? '-'}</td>
                <td className="px-2 py-1 text-right">{r.mean_leverage?.toFixed(2) ?? '-'}</td>
                <td className="px-2 py-1 text-right">{r.mean_per_day?.toFixed(3) ?? '-'}</td>
                <td className="px-2 py-1 text-right">{r.mean_per_week?.toFixed(3) ?? '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
