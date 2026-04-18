import { useState } from 'react'
import { Wand2, Copy, Download, Check, Loader2 } from 'lucide-react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

const ANALYSIS_TYPES = [
  { value: 'static', label: '静力分析', description: '线性或非线性静力学' },
  { value: 'dynamic', label: '动力分析', description: 'Explicit/Implicit 动力学' },
  { value: 'thermal', label: '热分析', description: '稳态或瞬态传热' },
  { value: 'coupled', label: '热力耦合', description: '热-结构耦合分析' },
  { value: 'modal', label: '模态分析', description: '固有频率提取' },
  { value: 'buckling', label: '屈曲分析', description: '线性/非线性屈曲' },
]

const ELEMENT_TYPES = [
  { value: 'C3D8R', label: 'C3D8R', description: '八节点六面体减缩积分' },
  { value: 'C3D10', label: 'C3D10', description: '十节点四面体' },
  { value: 'S4R', label: 'S4R', description: '四节点壳减缩积分' },
  { value: 'B31', label: 'B31', description: '两节点梁单元' },
  { value: 'CPE4R', label: 'CPE4R', description: '平面应变四节点' },
  { value: 'CPS4R', label: 'CPS4R', description: '平面应力四节点' },
]

export default function GeneratePage() {
  const [description, setDescription] = useState('')
  const [analysisType, setAnalysisType] = useState('static')
  const [elementType, setElementType] = useState('C3D8R')
  const [generateType, setGenerateType] = useState<'inp' | 'python'>('inp')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedCode, setGeneratedCode] = useState('')
  const [copied, setCopied] = useState(false)

  const handleGenerate = async () => {
    if (!description.trim()) return

    setIsGenerating(true)
    setGeneratedCode('')

    try {
      const response = await fetch(`/api/v1/generate/${generateType}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description,
          analysis_type: analysisType,
          element_type: elementType,
        }),
      })

      if (!response.ok) throw new Error('生成失败')

      const data = await response.json()
      setGeneratedCode(data.code || data.content)
    } catch (error) {
      console.error('Generation error:', error)
      setGeneratedCode('# 生成失败，请检查输入并重试')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleCopy = async () => {
    await navigator.clipboard.writeText(generatedCode)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const blob = new Blob([generatedCode], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = generateType === 'inp' ? 'model.inp' : 'script.py'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-2">模型生成</h2>
        <p className="text-dark-400">
          描述您要创建的模型，AI 将自动生成 Abaqus INP 文件或 Python 脚本
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Input panel */}
        <div className="space-y-6">
          {/* Generate type */}
          <div className="card">
            <h3 className="font-medium mb-4">生成类型</h3>
            <div className="flex gap-3">
              <button
                onClick={() => setGenerateType('inp')}
                className={`flex-1 py-3 px-4 rounded-lg border transition-colors ${
                  generateType === 'inp'
                    ? 'border-primary-500 bg-primary-500/10 text-primary-400'
                    : 'border-dark-700 hover:border-dark-600'
                }`}
              >
                <p className="font-medium">INP 文件</p>
                <p className="text-sm text-dark-400">原生输入文件</p>
              </button>
              <button
                onClick={() => setGenerateType('python')}
                className={`flex-1 py-3 px-4 rounded-lg border transition-colors ${
                  generateType === 'python'
                    ? 'border-primary-500 bg-primary-500/10 text-primary-400'
                    : 'border-dark-700 hover:border-dark-600'
                }`}
              >
                <p className="font-medium">Python 脚本</p>
                <p className="text-sm text-dark-400">Abaqus/CAE 脚本</p>
              </button>
            </div>
          </div>

          {/* Description */}
          <div className="card">
            <h3 className="font-medium mb-4">模型描述</h3>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="详细描述您要创建的模型，例如：&#10;创建一个简支梁模型，跨度 10m，截面 0.3m x 0.5m，材料为 C30 混凝土，施加均布荷载 10 kN/m..."
              rows={6}
              className="input resize-none"
            />
          </div>

          {/* Analysis type */}
          <div className="card">
            <h3 className="font-medium mb-4">分析类型</h3>
            <div className="grid grid-cols-2 gap-2">
              {ANALYSIS_TYPES.map((type) => (
                <button
                  key={type.value}
                  onClick={() => setAnalysisType(type.value)}
                  className={`p-3 rounded-lg border text-left transition-colors ${
                    analysisType === type.value
                      ? 'border-primary-500 bg-primary-500/10'
                      : 'border-dark-700 hover:border-dark-600'
                  }`}
                >
                  <p className="font-medium text-sm">{type.label}</p>
                  <p className="text-xs text-dark-400">{type.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Element type */}
          <div className="card">
            <h3 className="font-medium mb-4">单元类型</h3>
            <div className="grid grid-cols-3 gap-2">
              {ELEMENT_TYPES.map((type) => (
                <button
                  key={type.value}
                  onClick={() => setElementType(type.value)}
                  className={`p-2 rounded-lg border text-center transition-colors ${
                    elementType === type.value
                      ? 'border-primary-500 bg-primary-500/10'
                      : 'border-dark-700 hover:border-dark-600'
                  }`}
                >
                  <p className="font-mono text-sm">{type.value}</p>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={!description.trim() || isGenerating}
            className="btn btn-primary w-full py-3"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                正在生成...
              </>
            ) : (
              <>
                <Wand2 className="w-5 h-5 mr-2" />
                生成代码
              </>
            )}
          </button>
        </div>

        {/* Output panel */}
        <div className="card flex flex-col h-[calc(100vh-12rem)]">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium">生成结果</h3>
            {generatedCode && (
              <div className="flex gap-2">
                <button
                  onClick={handleCopy}
                  className="btn btn-secondary text-sm py-1.5"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4 mr-1" />
                      已复制
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4 mr-1" />
                      复制
                    </>
                  )}
                </button>
                <button
                  onClick={handleDownload}
                  className="btn btn-secondary text-sm py-1.5"
                >
                  <Download className="w-4 h-4 mr-1" />
                  下载
                </button>
              </div>
            )}
          </div>
          <div className="flex-1 overflow-auto bg-dark-950 rounded-lg">
            {generatedCode ? (
              <SyntaxHighlighter
                language={generateType === 'python' ? 'python' : 'ini'}
                style={oneDark}
                customStyle={{
                  margin: 0,
                  padding: '1rem',
                  background: 'transparent',
                  fontSize: '0.875rem',
                }}
              >
                {generatedCode}
              </SyntaxHighlighter>
            ) : (
              <div className="flex items-center justify-center h-full text-dark-500">
                生成的代码将显示在这里
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
