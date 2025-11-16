import React, { useState, useEffect, useRef } from 'react';
import { Search, Download, FileText, X, ChevronDown, Loader2, Settings, CheckCircle, ChevronUp, Check } from 'lucide-react';
import { apiService } from '../services/api';
import CustomScrollbar from './CustomScrollbar';
import VoiceRecorder from './VoiceRecorder';

interface AIPoweredSearchProps {
  onClose?: () => void;
  documentId?: string | null;
  documentName?: string;
  showDocumentInfo?: boolean;
}

const AIPoweredSearch: React.FC<AIPoweredSearchProps> = ({ 
  onClose,
  documentId,
  documentName,
  showDocumentInfo = true
}) => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [sources, setSources] = useState<Array<{filename: string; chunk_index: number; similarity: number}>>([]);
  const [history, setHistory] = useState<Array<{query: string, response: string, sources: Array<{filename: string; chunk_index: number; similarity: number}>}>>([]);
  const [currentHistoryIndex, setCurrentHistoryIndex] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showRawContent, setShowRawContent] = useState(false);
  const [exportFormat, setExportFormat] = useState('markdown');
  const [error, setError] = useState('');
  const [exportFormatSearch, setExportFormatSearch] = useState('');
  const [isExportFormatDropdownOpen, setIsExportFormatDropdownOpen] = useState(false);
  const [statistics, setStatistics] = useState<{totalDocuments: number; totalChunks: number} | null>(null);

  const exportFormats = [
    { value: 'markdown', label: 'Markdown' },
    { value: 'txt', label: 'Text File' },
  ];

  // Add ref for auto-scroll functionality
  const aiResponseRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to AI Response when it's generated
  useEffect(() => {
    if (response && aiResponseRef.current) {
      setTimeout(() => {
        aiResponseRef.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }, 100);
    }
  }, [response]);

  // Load statistics on mount
  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      const stats = await apiService.getStatistics();
      if (stats.success) {
        setStatistics({
          totalDocuments: stats.totalDocuments || 0,
          totalChunks: stats.totalChunks || 0
        });
      }
    } catch (err) {
      console.error('Error loading statistics:', err);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a question.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const result = await apiService.askQuestion(query);

      if (result.success) {
        setResponse(result.answer);
        setSources(result.sources || []);
        // Add to history
        setHistory(prev => [{ query, response: result.answer, sources: result.sources || [] }, ...prev]);
        setCurrentHistoryIndex(0);
        // Reload statistics
        loadStatistics();
      } else {
        setError(result.error || 'Failed to generate AI response. Please try again.');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate AI response. Please try again.');
      console.error('Error generating response:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // When currentHistoryIndex changes, update displayed response/query/sources
  useEffect(() => {
    if (currentHistoryIndex !== null && history[currentHistoryIndex]) {
      setResponse(history[currentHistoryIndex].response);
      setQuery(history[currentHistoryIndex].query);
      setSources(history[currentHistoryIndex].sources);
    }
  }, [currentHistoryIndex, history]);

  const exportResponse = async (format: string) => {
    if (!response) return;

    try {
      const blob = await apiService.exportContent(response, format, 'ai-search-response');
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ai-search-response.${format === 'markdown' ? 'md' : 'txt'}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to export file. Please try again.');
      console.error('Error exporting:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-6 text-white mb-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Search className="w-8 h-8" />
              <div>
                <h2 className="text-2xl font-bold">AI-Powered Document Search</h2>
                <p className="text-blue-100/90">Ask questions about your uploaded documents</p>
              </div>
            </div>
            {onClose && (
              <button 
                onClick={onClose} 
                className="text-white hover:bg-white/10 rounded-full p-2 transition-colors"
                title="Close"
                aria-label="Close search"
              >
                <X className="w-6 h-6" />
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Search Configuration */}
          <div className="space-y-6">
            <div className="bg-white/80 backdrop-blur-xl rounded-xl p-6 border border-white/20 shadow-lg">
              <h3 className="font-semibold text-gray-800 mb-4 flex items-center text-lg">
                <Settings className="w-5 h-5 mr-2" />
                Search Configuration
              </h3>
              
              {/* Statistics */}
              {statistics && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-gray-700">
                    <span className="font-semibold">{statistics.totalDocuments}</span> document(s) processed
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="font-semibold">{statistics.totalChunks}</span> chunks available
                  </p>
                </div>
              )}

              {/* Document Info */}
              {showDocumentInfo && documentName && (
                <div className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-sm font-medium text-gray-700">Current Document:</p>
                  <p className="text-sm text-gray-600">{documentName}</p>
                </div>
              )}

              {/* Query Input */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Question
                </label>
                <VoiceRecorder
                  value={query}
                  onChange={setQuery}
                  onConfirm={setQuery}
                  inputPlaceholder="What would you like to know about the documents?"
                />
              </div>

              {/* Search Button */}
              <button
                onClick={handleSearch}
                disabled={!query.trim() || isLoading}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center space-x-2 transition-colors shadow-md"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Generating AI Response...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    <span>Generate AI Response</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            {/* History Dropdown */}
            {history.length > 0 && (
              <div className="mb-2 flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">History:</label>
                <select
                  className="border border-gray-300 rounded px-2 py-1 text-sm bg-white"
                  value={currentHistoryIndex ?? 0}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setCurrentHistoryIndex(Number(e.target.value))}
                  title="Select previous query"
                  aria-label="Select previous query from history"
                >
                  {history.map((item: {query: string, response: string, sources: Array<{filename: string; chunk_index: number; similarity: number}>}, idx: number) => (
                    <option key={idx} value={idx}>
                      {item.query.length > 40 ? item.query.slice(0, 40) + '...' : item.query}
                    </option>
                  ))}
                </select>
                {currentHistoryIndex !== null && currentHistoryIndex !== 0 && (
                  <button
                    className="text-xs text-blue-600 underline ml-2"
                    onClick={() => setCurrentHistoryIndex(0)}
                  >
                    Go to Latest
                  </button>
                )}
              </div>
            )}

            {error && (
              <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                {error}
              </div>
            )}

            {response && (
              <div className="bg-white/80 backdrop-blur-xl rounded-xl p-6 border border-white/20 shadow-lg" ref={aiResponseRef}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-gray-800 text-lg">AI Response</h3>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setShowRawContent(!showRawContent)}
                      className="text-sm text-blue-600 hover:underline"
                    >
                      {showRawContent ? 'Show Formatted' : 'Show Raw Content'}
                    </button>
                  </div>
                </div>
                
                <div className="bg-white/70 rounded-lg p-4 border border-gray-200 max-h-96 overflow-y-auto mb-4">
                  {showRawContent ? (
                    <pre className="text-sm text-gray-700 whitespace-pre-wrap">{response}</pre>
                  ) : (
                    <div className="prose prose-sm max-w-none">
                      {response.split('\n').map((line, index) => {
                        if (line.startsWith('## ')) {
                          return <h2 key={index} className="text-lg font-bold text-gray-800 mt-4 mb-2">{line.substring(3)}</h2>;
                        } else if (line.startsWith('- **')) {
                          const match = line.match(/- \*\*(.*?)\*\*: (.*)/);
                          if (match) {
                            return <p key={index} className="mb-2"><strong>{match[1]}:</strong> {match[2]}</p>;
                          }
                        } else if (line.startsWith('- ')) {
                          return <p key={index} className="mb-1 ml-4">• {line.substring(2)}</p>;
                        } else if (line.trim()) {
                          return <p key={index} className="mb-2 text-gray-700">{line}</p>;
                        }
                        return <br key={index} />;
                      })}
                    </div>
                  )}
                </div>

                {/* Sources */}
                {sources.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Sources:</h4>
                    <div className="space-y-2">
                      {sources.map((source, idx) => (
                        <div key={idx} className="p-2 bg-gray-50 rounded border border-gray-200 text-sm">
                          <p className="font-medium text-gray-700">{source.filename}</p>
                          <p className="text-xs text-gray-500">Chunk {source.chunk_index} • Similarity: {source.similarity}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Export Options */}
                <div className="mt-4 space-y-3">
                  <div className="flex items-center space-x-2">
                    <label className="text-sm font-medium text-gray-700">Export Format:</label>
                    <div className="relative w-48">
                      <button
                        type="button"
                        onClick={() => setIsExportFormatDropdownOpen(!isExportFormatDropdownOpen)}
                        className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 bg-white w-full flex items-center justify-between"
                      >
                        <span>{exportFormats.find(f => f.value === exportFormat)?.label || 'Select format'}</span>
                        {isExportFormatDropdownOpen ? (
                          <ChevronUp className="w-4 h-4 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-gray-400" />
                        )}
                      </button>
                      {isExportFormatDropdownOpen && (
                        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-xl max-h-48 overflow-hidden">
                          <div className="p-2 border-b border-gray-200 bg-gray-50">
                            <input
                              type="text"
                              value={exportFormatSearch}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setExportFormatSearch(e.target.value)}
                              placeholder="Search formats..."
                              className="w-full px-2 py-1 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white placeholder-gray-400"
                            />
                          </div>
                          <div className="max-h-32 overflow-y-auto">
                            {exportFormats.filter(f => f.label.toLowerCase().includes(exportFormatSearch.toLowerCase())).length === 0 ? (
                              <div className="p-2 text-gray-500 text-sm text-center">No formats found</div>
                            ) : (
                              exportFormats.filter(f => f.label.toLowerCase().includes(exportFormatSearch.toLowerCase())).map(f => (
                                <button
                                  key={f.value}
                                  type="button"
                                  onClick={() => { setExportFormat(f.value); setIsExportFormatDropdownOpen(false); setExportFormatSearch(''); }}
                                  className={`w-full text-left flex items-center space-x-2 p-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0 ${exportFormat === f.value ? 'bg-blue-50' : ''}`}
                                >
                                  <span className="text-sm text-gray-700 flex-1">{f.label}</span>
                                  {exportFormat === f.value && <Check className="w-4 h-4 text-blue-600" />}
                                </button>
                              ))
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <button
                    onClick={() => exportResponse(exportFormat)}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    <span>Export</span>
                  </button>
                </div>
              </div>
            )}

            {!response && !isLoading && (
              <div className="bg-white/80 backdrop-blur-xl rounded-xl p-8 text-center border border-white/20 shadow-lg">
                <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-600 mb-2">Ready to Search</h3>
                <p className="text-gray-500">Enter your question and click "Generate AI Response" to get started.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIPoweredSearch;

