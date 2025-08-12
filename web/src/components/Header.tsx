import React from 'react'

type Props = {
  mode: 'channels' | 'symbols'
  setMode: (m: 'channels' | 'symbols') => void
  page: 'viewer' | 'stats'
  setPage: (p: 'viewer' | 'stats') => void
}

export default function Header({ mode, setMode, page, setPage }: Props) {
  const tabClass = (active: boolean) =>
    `px-3 py-1 rounded text-sm ${active ? 'bg-black text-white' : 'bg-neutral-100'}`

  return (
    <header className="w-full border-b bg-white">
      <div className="mx-auto max-w-7xl px-3 py-2 flex items-center gap-2">
        <h1 className="text-lg font-semibold mr-auto">Signal Viewer</h1>

        {/* Primary page tabs */}
        <nav className="flex items-center gap-2 text-sm">
          <button className={tabClass(page === 'viewer')} onClick={() => setPage('viewer')}>
            Viewer
          </button>
          <button className={tabClass(page === 'stats')} onClick={() => setPage('stats')}>
            Statistics
          </button>
        </nav>

        {/* Unified mode toggle — styled the same size/appearance as page tabs */}
        <div className="ml-2 flex items-center gap-2">
          <button
            className={tabClass(mode === 'channels')}
            onClick={() => setMode('channels')}
            aria-pressed={mode === 'channels'}
          >
            Channels
          </button>
          <button
            className={tabClass(mode === 'symbols')}
            onClick={() => setMode('symbols')}
            aria-pressed={mode === 'symbols'}
          >
            Symbols
          </button>
        </div>
      </div>
    </header>
  )
}
