'use client';

interface ModelOption {
  id: string;
  name: string;
  description?: string;
}

interface ModelSelectorProps {
  selectedModel: string;
  onModelChange: (modelId: string) => void;
  disabled?: boolean;
}

const models: ModelOption[] = [
  {
    id: 'audio-flamingo-3',
    name: 'Audio Flamingo 3',
    description: 'Advanced audio reasoning model',
  },
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    description: 'OpenAI\'s latest multimodal model',
  },
  {
    id: 'llama',
    name: 'Llama',
    description: 'Meta\'s open-source language model',
  },
  {
    id: 'gemini',
    name: 'Gemini',
    description: 'Google\'s multimodal AI model',
  },
];

export default function ModelSelector({ selectedModel, onModelChange, disabled = false }: ModelSelectorProps) {
  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-300 mb-2">
        Select AI Model
      </label>
      <select
        value={selectedModel}
        onChange={(e) => onModelChange(e.target.value)}
        disabled={disabled}
        className="w-full px-4 py-3 bg-dark-800 border border-dark-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {models.map((model) => (
          <option key={model.id} value={model.id}>
            {model.name}
          </option>
        ))}
      </select>
      {models.find(m => m.id === selectedModel)?.description && (
        <p className="mt-2 text-xs text-gray-500">
          {models.find(m => m.id === selectedModel)?.description}
        </p>
      )}
    </div>
  );
}

