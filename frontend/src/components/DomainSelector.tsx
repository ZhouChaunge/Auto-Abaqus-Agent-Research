interface Domain {
  value: string
  label: string
  description: string
}

interface DomainSelectorProps {
  domains: Domain[]
  value: string
  onChange: (value: string) => void
}

export default function DomainSelector({ domains, value, onChange }: DomainSelectorProps) {
  return (
    <div>
      <label className="block text-sm font-medium mb-3">领域选择</label>
      <div className="flex flex-wrap gap-2">
        {domains.map((domain) => (
          <button
            key={domain.value}
            onClick={() => onChange(domain.value)}
            className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
              value === domain.value
                ? 'bg-primary-600 text-white'
                : 'bg-dark-800 text-dark-300 hover:bg-dark-700'
            }`}
            title={domain.description}
          >
            {domain.label}
          </button>
        ))}
      </div>
    </div>
  )
}
