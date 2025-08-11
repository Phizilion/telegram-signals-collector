import React from 'react'
import type { ChannelItem, SymbolItem } from '../api'

interface Props {
  mode: 'channels' | 'symbols'
  items: (ChannelItem | SymbolItem)[]
  selected: string | number | null
  onSelect: (id: string | number) => void
}

export default function Sidebar({ mode, items, selected, onSelect }: Props) {
  return (
    <aside className="sidebar border-r h-full scroll-y">
      <ul className="divide-y">
        {items.map((it) => {
          const key = 'symbol' in it ? it.symbol : it.id
          const label = 'symbol' in it ? it.symbol : (it.title || it.username || it.id)
          const total = it.total
          const active = selected === key
          return (
            <li key={String(key)}>
              <button
                className={`w-full text-left px-3 py-2 ${active?'bg-neutral-200':'hover:bg-neutral-100'}`}
                onClick={() => onSelect(key)}
              >
                <div className="flex items-center justify-between">
                  <span className="truncate text-sm">{label}</span>
                  <span className="text-xs text-neutral-600">{total}</span>
                </div>
              </button>
            </li>
          )
        })}
      </ul>
    </aside>
  )
}
