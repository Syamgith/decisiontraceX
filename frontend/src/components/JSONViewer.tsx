import { useState } from 'react'

interface JSONViewerProps {
  data: any
  title: string
  collapsed?: boolean
}

function JSONViewer({ data, title, collapsed = false }: JSONViewerProps) {
  const [isCollapsed, setIsCollapsed] = useState(collapsed)
  const [isCopied, setIsCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2))
    setIsCopied(true)
    setTimeout(() => setIsCopied(false), 2000)
  }

  const syntaxHighlight = (json: string) => {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    return json.replace(
      /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
      (match) => {
        let cls = 'text-orange-600' // number
        if (/^"/.test(match)) {
          if (/:$/.test(match)) {
            cls = 'text-blue-600 font-semibold' // key
          } else {
            cls = 'text-green-600' // string
          }
        } else if (/true|false/.test(match)) {
          cls = 'text-purple-600' // boolean
        } else if (/null/.test(match)) {
          cls = 'text-gray-500' // null
        }
        return `<span class="${cls}">${match}</span>`
      }
    )
  }

  const jsonString = JSON.stringify(data, null, 2)

  return (
    <div className="mt-4">
      <div className="flex items-center justify-between mb-2">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="flex items-center text-sm font-semibold text-gray-700 hover:text-gray-900"
        >
          <span className="mr-2">{isCollapsed ? '▶' : '▼'}</span>
          {title}
          <span className="ml-2 text-xs text-gray-500 font-normal">
            ({Object.keys(data).length} {Object.keys(data).length === 1 ? 'key' : 'keys'})
          </span>
        </button>
        <button
          onClick={handleCopy}
          className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 rounded transition-colors"
        >
          {isCopied ? '✓ Copied' : '📋 Copy'}
        </button>
      </div>

      {!isCollapsed && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 overflow-x-auto">
          <pre
            className="text-xs leading-relaxed"
            dangerouslySetInnerHTML={{ __html: syntaxHighlight(jsonString) }}
          />
        </div>
      )}
    </div>
  )
}

export default JSONViewer
