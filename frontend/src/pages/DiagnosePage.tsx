import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, AlertCircle, CheckCircle, Loader2, X } from 'lucide-react'

interface DiagnosisResult {
  success: boolean
  errors: Array<{
    code: string
    severity: string
    message: string
    location?: string
    suggestion: string
  }>
  suggestions: string[]
  summary: string
}

export default function DiagnosePage() {
  const [files, setFiles] = useState<File[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<DiagnosisResult | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(acceptedFiles)
    setResult(null)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.msg', '.sta', '.inp', '.dat', '.log'],
    },
    maxFiles: 5,
  })

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleAnalyze = async () => {
    if (files.length === 0) return

    setIsAnalyzing(true)
    try {
      const formData = new FormData()
      files.forEach((file) => formData.append('files', file))

      const response = await fetch('/api/v1/diagnose/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error('分析失败')

      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error('Diagnosis error:', error)
      setResult({
        success: false,
        errors: [
          {
            code: 'UPLOAD_ERROR',
            severity: 'error',
            message: '文件上传或分析失败',
            suggestion: '请检查文件格式是否正确，稍后重试',
          },
        ],
        suggestions: [],
        summary: '分析过程中发生错误',
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error':
        return 'text-red-400 bg-red-400/10'
      case 'warning':
        return 'text-yellow-400 bg-yellow-400/10'
      case 'info':
        return 'text-blue-400 bg-blue-400/10'
      default:
        return 'text-dark-400 bg-dark-400/10'
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-2">错误诊断</h2>
        <p className="text-dark-400">
          上传 Abaqus 输出文件 (.msg, .sta, .dat, .log)，AI 将自动分析错误并提供解决方案
        </p>
      </div>

      {/* Upload area */}
      <div
        {...getRootProps()}
        className={`card cursor-pointer border-2 border-dashed transition-colors ${
          isDragActive
            ? 'border-primary-500 bg-primary-500/5'
            : 'border-dark-700 hover:border-dark-600'
        }`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center py-8">
          <Upload
            className={`w-12 h-12 mb-4 ${
              isDragActive ? 'text-primary-400' : 'text-dark-500'
            }`}
          />
          <p className="text-lg font-medium mb-1">
            {isDragActive ? '放下文件' : '拖放文件到此处'}
          </p>
          <p className="text-dark-400 text-sm">
            或点击选择文件 (支持 .msg, .sta, .inp, .dat, .log)
          </p>
        </div>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between bg-dark-800 rounded-lg px-4 py-3"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-primary-400" />
                <div>
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-dark-400">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
              <button
                onClick={() => removeFile(index)}
                className="p-1 hover:bg-dark-700 rounded transition-colors"
              >
                <X className="w-4 h-4 text-dark-400" />
              </button>
            </div>
          ))}
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="btn btn-primary w-full mt-4"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                正在分析...
              </>
            ) : (
              '开始诊断'
            )}
          </button>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="mt-8 space-y-6">
          {/* Summary */}
          <div className="card">
            <div className="flex items-start gap-4">
              {result.success ? (
                <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-0.5" />
              )}
              <div>
                <h3 className="font-semibold text-lg mb-2">诊断摘要</h3>
                <p className="text-dark-300">{result.summary}</p>
              </div>
            </div>
          </div>

          {/* Errors */}
          {result.errors.length > 0 && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">发现的问题</h3>
              {result.errors.map((error, index) => (
                <div key={index} className="card">
                  <div className="flex items-start gap-4">
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(
                        error.severity
                      )}`}
                    >
                      {error.code}
                    </span>
                    <div className="flex-1">
                      <p className="font-medium mb-1">{error.message}</p>
                      {error.location && (
                        <p className="text-sm text-dark-400 mb-2">
                          位置: {error.location}
                        </p>
                      )}
                      <div className="bg-dark-800 rounded-lg p-3 mt-2">
                        <p className="text-sm text-primary-400 font-medium mb-1">
                          💡 建议解决方案:
                        </p>
                        <p className="text-sm text-dark-300">{error.suggestion}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Suggestions */}
          {result.suggestions.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-lg mb-4">优化建议</h3>
              <ul className="space-y-2">
                {result.suggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-primary-400">•</span>
                    <span className="text-dark-300">{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
