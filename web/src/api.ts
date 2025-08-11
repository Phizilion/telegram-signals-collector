export type ChannelItem = { id: number; title?: string | null; username?: string | null; total: number }
export type SymbolItem = { symbol: string; total: number }
export type SignalItem = {
  id: number; channel_id: number; message_id: number; message_date: string;
  symbol: string; side: 'long' | 'short'; leverage?: number | null;
  stop_loss?: number[] | null; take_profits: number[]; original_text: string;
}
export type ChannelStats = {
  channel_id: number; title?: string | null; username?: string | null;
  total: number; long_count: number; short_count: number; long_short_ratio?: number | null;
  mean_leverage?: number | null; mean_per_day?: number | null; mean_per_week?: number | null;
}
export type SymbolStats = {
  symbol: string; total: number; long_count: number; short_count: number; long_short_ratio?: number | null;
  mean_leverage?: number | null; mean_per_day?: number | null; mean_per_week?: number | null;
}

const get = async <T>(url: string): Promise<T> => {
  const r = await fetch(url)
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return await r.json()
}

export const api = {
  channels: () => get<ChannelItem[]>('/api/channels'),
  symbols: () => get<SymbolItem[]>('/api/symbols'),
  channelSignals: (id: number, limit = 100, offset = 0) => get<SignalItem[]>(`/api/channels/${id}/signals?limit=${limit}&offset=${offset}`),
  symbolSignals: (sym: string, limit = 100, offset = 0) => get<SignalItem[]>(`/api/symbols/${encodeURIComponent(sym)}/signals?limit=${limit}&offset=${offset}`),
  channelStats: () => get<ChannelStats[]>('/api/stats/channels'),
  symbolStats: () => get<SymbolStats[]>('/api/stats/symbols'),
}
