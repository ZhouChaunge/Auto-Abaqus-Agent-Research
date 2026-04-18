import { useState } from 'react'
import { Plus, Trash2, MessageSquare } from 'lucide-react'

export interface ConversationSummary {
  id: string
  title: string
  domain: string
  message_count: number
  created_at: string
  updated_at: string
}

interface Props {
  conversations: ConversationSummary[]
  activeId: string | null
  onSelect: (id: string) => void
  onNew: () => void
  onDelete: (id: string) => void
}

export default function ConversationSidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
}: Props) {
  const [hoveredId, setHoveredId] = useState<string | null>(null)

  const formatTime = (iso: string) => {
    const d = new Date(iso)
    const now = new Date()
    const diffMs = now.getTime() - d.getTime()
    const diffMin = Math.floor(diffMs / 60000)
    if (diffMin < 1) return '刚刚'
    if (diffMin < 60) return `${diffMin} 分钟前`
    const diffHour = Math.floor(diffMin / 60)
    if (diffHour < 24) return `${diffHour} 小时前`
    const diffDay = Math.floor(diffHour / 24)
    if (diffDay < 7) return `${diffDay} 天前`
    return d.toLocaleDateString()
  }

  return (
    <div className="flex flex-col h-full">
      {/* New conversation button */}
      <div className="p-3">
        <button
          onClick={onNew}
          className="flex items-center gap-2 w-full px-3 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors text-sm font-medium"
        >
          <Plus className="w-4 h-4" />
          新建对话
        </button>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-1">
        {conversations.length === 0 ? (
          <div className="text-center py-8 text-dark-500 text-sm">
            暂无对话记录
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                activeId === conv.id
                  ? 'bg-primary-600/15 text-primary-400'
                  : 'text-dark-300 hover:bg-dark-800'
              }`}
              onClick={() => onSelect(conv.id)}
              onMouseEnter={() => setHoveredId(conv.id)}
              onMouseLeave={() => setHoveredId(null)}
            >
              <MessageSquare className="w-4 h-4 flex-shrink-0 opacity-50" />
              <div className="flex-1 min-w-0">
                <p className="text-sm truncate">{conv.title}</p>
                <p className="text-xs text-dark-500 truncate">
                  {formatTime(conv.updated_at)}
                </p>
              </div>
              {hoveredId === conv.id && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete(conv.id)
                  }}
                  className="p-1 rounded hover:bg-dark-700 text-dark-500 hover:text-red-400 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
