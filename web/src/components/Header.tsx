import React from 'react'

type Props = { mode: 'channels' | 'symbols'; setMode: (m: 'channels' | 'symbols') => void; page: 'viewer' | 'stats'; setPage: (p: 'viewer' | 'stats') => void }

export default function Header({ mode, setMode, page, setPage }: Props) {
  return (
    <header className="w-full border-b bg-white">
      <div className="mx-auto max-w-7xl px-3 py-2 flex items-center gap-2">
        <h1 className="text-lg font-semibold mr-auto">Signal Viewer</h1>
        <nav className="flex items-center gap-1 text-sm">
          <button className={`px-3 py-1 rounded ${page==='viewer'?'bg-black text-white':'bg-neutral-100'}`} onClick={()=>setPage('viewer')}>Viewer</button>
          <button className={`px-3 py-1 rounded ${page==='stats'?'bg-black text-white':'bg-neutral-100'}`} onClick={()=>setPage('stats')}>Statistics</button>
        </nav>
        <div className="ml-2">
          <button className="px-3 py-1 rounded-l bg-neutral-200" onClick={()=>setMode('channels')} aria-pressed={mode==='channels'}>Channels</button>
          <button className="px-3 py-1 rounded-r bg-neutral-200" onClick={()=>setMode('symbols')} aria-pressed={mode==='symbols'}>Symbols</button>
        </div>
      </div>
    </header>
  )
}
