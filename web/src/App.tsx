import React, { useEffect, useState } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import SignalList from './components/SignalList'
import StatsPage from './components/StatsPage'
import { api, ChannelItem, SymbolItem, SignalItem } from './api'

export default function App() {
  const [mode, setMode] = useState<'channels' | 'symbols'>('channels')
  const [page, setPage] = useState<'viewer' | 'stats'>('viewer')
  const [items, setItems] = useState<(ChannelItem | SymbolItem)[]>([])
  const [selected, setSelected] = useState<string | number | null>(null)
  const [signals, setSignals] = useState<SignalItem[]>([])

  const loadItems = async () => {
    const data = mode === 'channels' ? await api.channels() : await api.symbols()
    setItems(data)
    if (!selected && data.length) {
      const key = mode === 'channels' ? (data[0] as ChannelItem).id : (data[0] as SymbolItem).symbol
      setSelected(key)
    }
  }

  const loadSignals = async () => {
    if (selected == null) return
    const rows = mode === 'channels'
      ? await api.channelSignals(selected as number)
      : await api.symbolSignals(String(selected))
    setSignals(rows)
  }

  useEffect(() => { loadItems() }, [mode])
  useEffect(() => { loadSignals() }, [selected, mode])

  return (
    <div className="h-dvh flex flex-col">
      <Header mode={mode} setMode={(m)=>{setSelected(null); setMode(m)}} page={page} setPage={setPage} />
      {page === 'stats' ? (
        <main className="flex-1">
          <StatsPage mode={mode} />
        </main>
      ) : (
        <main className="flex-1 grid md:grid-cols-[320px,1fr]">
          <Sidebar mode={mode} items={items} selected={selected} onSelect={setSelected} />
          <section className="h-full overflow-y-auto">
            <SignalList rows={signals} showChannel={mode === 'symbols'} />
          </section>
        </main>
      )}
    </div>
  )
}
