import React from 'react'

type Props = { mode: 'channels' | 'symbols'; setMode: (m: 'channels' | 'symbols') => void }

export default function ModeToggle({ mode, setMode }: Props) {
  return (
    <div className="inline-flex rounded overflow-hidden border">
      <button className={`px-3 py-1 ${mode==='channels'?'bg-black text-white':'bg-white'}`} onClick={()=>setMode('channels')}>Channels</button>
      <button className={`px-3 py-1 ${mode==='symbols'?'bg-black text-white':'bg-white'}`} onClick={()=>setMode('symbols')}>Symbols</button>
    </div>
  )
}
