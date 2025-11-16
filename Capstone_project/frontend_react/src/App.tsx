import { useState, useEffect } from 'react';
import { Search, Upload, MessageSquare, Wifi, WifiOff, AlertCircle } from 'lucide-react';
import DocumentUpload from './components/DocumentUpload';
import QuestionAnswer from './components/QuestionAnswer';
import AIPoweredSearch from './components/AIPoweredSearch';
import { checkBackendHealth } from './services/api';

type ViewMode = 'upload' | 'qa' | 'search';

function App() {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [documentName, setDocumentName] = useState<string>('');
  const [viewMode, setViewMode] = useState<ViewMode>('upload');
  const [isBackendConnected, setIsBackendConnected] = useState<boolean | null>(null);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  const handleDocumentUploaded = (id: string, name: string) => {
    setDocumentId(id);
    setDocumentName(name);
    setViewMode('search'); // Switch to search view after upload
  };

  const handleReset = () => {
    setDocumentId(null);
    setDocumentName('');
    setViewMode('upload');
  };

  // Check backend connection on mount and periodically
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const connected = await checkBackendHealth();
        setIsBackendConnected(connected);
        if (!connected) {
          setConnectionError('Backend server is not reachable. Please ensure the backend is running on http://localhost:8000');
        } else {
          setConnectionError(null);
        }
      } catch (error: any) {
        setIsBackendConnected(false);
        setConnectionError(error.message || 'Failed to connect to backend server');
      }
    };

    // Check immediately
    checkConnection();

    // Check every 30 seconds
    const interval = setInterval(checkConnection, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Connection Status Banner */}
        {isBackendConnected === false && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium text-red-800">Backend Connection Error</p>
              <p className="text-xs text-red-600 mt-1">{connectionError}</p>
            </div>
            <WifiOff className="w-5 h-5 text-red-600 flex-shrink-0" />
          </div>
        )}
        {isBackendConnected === true && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-2">
            <Wifi className="w-4 h-4 text-green-600" />
            <p className="text-sm text-green-800">Backend connected</p>
          </div>
        )}

        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Intelligent Document Assistant
          </h1>
          <p className="text-gray-600">
            Upload documents and interact with them using AI-powered RAG search
          </p>
        </header>

        {/* Navigation Tabs */}
        <div className="mb-6 flex space-x-2 border-b border-gray-200">
          <button
            onClick={() => setViewMode('upload')}
            className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${
              viewMode === 'upload'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Upload className="w-4 h-4 inline mr-2" />
            Upload
          </button>
          {documentId && (
            <>
              <button
                onClick={() => setViewMode('search')}
                className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${
                  viewMode === 'search'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Search className="w-4 h-4 inline mr-2" />
                AI Search
              </button>
              <button
                onClick={() => setViewMode('qa')}
                className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${
                  viewMode === 'qa'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <MessageSquare className="w-4 h-4 inline mr-2" />
                Q&A Chat
              </button>
            </>
          )}
        </div>

        <main>
          {viewMode === 'upload' && (
            <DocumentUpload onDocumentUploaded={handleDocumentUploaded} />
          )}
          {viewMode === 'search' && (
            <AIPoweredSearch
              documentId={documentId}
              documentName={documentName}
              onClose={handleReset}
              showDocumentInfo={!!documentId}
            />
          )}
          {viewMode === 'qa' && documentId && (
            <QuestionAnswer
              documentId={documentId}
              documentName={documentName}
              onReset={handleReset}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
