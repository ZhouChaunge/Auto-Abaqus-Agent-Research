import { useState, useEffect } from 'react'
import { Search, BookOpen, AlertTriangle, Box, ChevronRight } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

interface ErrorInfo {
  code: string
  name: string
  description: string
  causes: string[]
  solutions: string[]
}

interface ElementInfo {
  name: string
  type: string
  description: string
  nodes: number
  integration_points: number
  applications: string[]
  tips: string[]
}

const TABS = [
  { id: 'errors', label: '错误代码', icon: AlertTriangle },
  { id: 'elements', label: '单元库', icon: Box },
  { id: 'domains', label: '领域知识', icon: BookOpen },
]

const DOMAINS = [
  { id: 'geotechnical', name: '岩土工程', icon: '🏔️' },
  { id: 'structural', name: '结构工程', icon: '🏗️' },
  { id: 'mechanical', name: '机械工程', icon: '⚙️' },
  { id: 'thermal', name: '热分析', icon: '🔥' },
  { id: 'impact', name: '冲击分析', icon: '💥' },
  { id: 'composite', name: '复合材料', icon: '🧬' },
  { id: 'biomechanics', name: '生物力学', icon: '🦴' },
  { id: 'electromagnetic', name: '电磁分析', icon: '⚡' },
]

export default function KnowledgePage() {
  const [activeTab, setActiveTab] = useState('errors')
  const [searchQuery, setSearchQuery] = useState('')
  const [errors, setErrors] = useState<ErrorInfo[]>([])
  const [elements, setElements] = useState<ElementInfo[]>([])
  const [selectedItem, setSelectedItem] = useState<ErrorInfo | ElementInfo | null>(null)
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null)
  const [domainContent, setDomainContent] = useState<string>('')

  useEffect(() => {
    fetchData()
  }, [activeTab])

  const fetchData = async () => {
    try {
      if (activeTab === 'errors') {
        const response = await fetch('/api/v1/knowledge/errors')
        const data = await response.json()
        setErrors(data.errors || [])
      } else if (activeTab === 'elements') {
        const response = await fetch('/api/v1/knowledge/elements')
        const data = await response.json()
        setElements(data.elements || [])
      }
    } catch (error) {
      console.error('Failed to fetch data:', error)
    }
  }

  const handleDomainClick = async (domainId: string) => {
    setSelectedDomain(domainId)
    try {
      const response = await fetch(`/api/v1/knowledge/domain/${domainId}`)
      const data = await response.json()
      setDomainContent(data.content || '暂无内容')
    } catch (error) {
      console.error('Failed to fetch domain content:', error)
      setDomainContent('加载失败')
    }
  }

  const filteredErrors = errors.filter(
    (e) =>
      e.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const filteredElements = elements.filter(
    (e) =>
      e.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-80 border-r border-dark-800 flex flex-col">
        {/* Tabs */}
        <div className="flex border-b border-dark-800">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id)
                setSelectedItem(null)
                setSelectedDomain(null)
              }}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-primary-400 border-b-2 border-primary-400'
                  : 'text-dark-400 hover:text-dark-200'
              }`}
            >
              <tab.icon className="w-4 h-4 mx-auto mb-1" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search */}
        {activeTab !== 'domains' && (
          <div className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索..."
                className="input pl-10"
              />
            </div>
          </div>
        )}

        {/* List */}
        <div className="flex-1 overflow-y-auto">
          {activeTab === 'errors' && (
            <div className="space-y-1 p-2">
              {filteredErrors.map((error) => (
                <button
                  key={error.code}
                  onClick={() => setSelectedItem(error)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                    selectedItem === error
                      ? 'bg-primary-600/10 text-primary-400'
                      : 'hover:bg-dark-800'
                  }`}
                >
                  <p className="font-mono text-sm text-primary-400">{error.code}</p>
                  <p className="text-sm truncate">{error.name}</p>
                </button>
              ))}
            </div>
          )}

          {activeTab === 'elements' && (
            <div className="space-y-1 p-2">
              {filteredElements.map((element) => (
                <button
                  key={element.name}
                  onClick={() => setSelectedItem(element)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                    selectedItem === element
                      ? 'bg-primary-600/10 text-primary-400'
                      : 'hover:bg-dark-800'
                  }`}
                >
                  <p className="font-mono text-sm text-primary-400">{element.name}</p>
                  <p className="text-sm truncate text-dark-400">{element.type}</p>
                </button>
              ))}
            </div>
          )}

          {activeTab === 'domains' && (
            <div className="space-y-1 p-2">
              {DOMAINS.map((domain) => (
                <button
                  key={domain.id}
                  onClick={() => handleDomainClick(domain.id)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors ${
                    selectedDomain === domain.id
                      ? 'bg-primary-600/10 text-primary-400'
                      : 'hover:bg-dark-800'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{domain.icon}</span>
                    <span>{domain.name}</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-dark-500" />
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'errors' && selectedItem && 'code' in selectedItem && (
          <div className="max-w-3xl">
            <div className="mb-6">
              <span className="inline-block px-3 py-1 bg-red-400/10 text-red-400 rounded-full text-sm font-mono mb-2">
                {selectedItem.code}
              </span>
              <h2 className="text-2xl font-semibold">{selectedItem.name}</h2>
            </div>

            <div className="card mb-6">
              <h3 className="font-medium mb-2">描述</h3>
              <p className="text-dark-300">{selectedItem.description}</p>
            </div>

            <div className="card mb-6">
              <h3 className="font-medium mb-3">常见原因</h3>
              <ul className="space-y-2">
                {selectedItem.causes.map((cause, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-yellow-400">•</span>
                    <span className="text-dark-300">{cause}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="card">
              <h3 className="font-medium mb-3">解决方案</h3>
              <ul className="space-y-2">
                {selectedItem.solutions.map((solution, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-green-400">✓</span>
                    <span className="text-dark-300">{solution}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'elements' && selectedItem && 'nodes' in selectedItem && (
          <div className="max-w-3xl">
            <div className="mb-6">
              <span className="inline-block px-3 py-1 bg-primary-400/10 text-primary-400 rounded-full text-sm font-mono mb-2">
                {selectedItem.name}
              </span>
              <h2 className="text-2xl font-semibold">{selectedItem.type}</h2>
            </div>

            <div className="card mb-6">
              <h3 className="font-medium mb-2">描述</h3>
              <p className="text-dark-300">{selectedItem.description}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="card">
                <p className="text-dark-400 text-sm">节点数</p>
                <p className="text-2xl font-semibold">{selectedItem.nodes}</p>
              </div>
              <div className="card">
                <p className="text-dark-400 text-sm">积分点数</p>
                <p className="text-2xl font-semibold">{selectedItem.integration_points}</p>
              </div>
            </div>

            <div className="card mb-6">
              <h3 className="font-medium mb-3">适用场景</h3>
              <ul className="space-y-2">
                {selectedItem.applications.map((app, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-primary-400">•</span>
                    <span className="text-dark-300">{app}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="card">
              <h3 className="font-medium mb-3">使用建议</h3>
              <ul className="space-y-2">
                {selectedItem.tips.map((tip, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-yellow-400">💡</span>
                    <span className="text-dark-300">{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'domains' && selectedDomain && (
          <div className="max-w-3xl prose prose-invert">
            <h2 className="text-2xl font-semibold mb-6">
              {DOMAINS.find((d) => d.id === selectedDomain)?.icon}{' '}
              {DOMAINS.find((d) => d.id === selectedDomain)?.name}
            </h2>
            <ReactMarkdown>{domainContent}</ReactMarkdown>
          </div>
        )}

        {!selectedItem && !selectedDomain && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <BookOpen className="w-16 h-16 text-dark-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">知识库</h3>
            <p className="text-dark-400 max-w-md">
              从左侧选择一个条目查看详细信息。包含错误代码解释、单元类型说明和领域专业知识。
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
