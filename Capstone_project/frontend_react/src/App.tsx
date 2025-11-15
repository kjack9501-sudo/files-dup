import { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import QuestionAnswer from './components/QuestionAnswer';

function App() {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [documentName, setDocumentName] = useState<string>('');

  const handleDocumentUploaded = (id: string, name: string) => {
    setDocumentId(id);
    setDocumentName(name);
  };

  const handleReset = () => {
    setDocumentId(null);
    setDocumentName('');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-12">
          <h1 className="text-3xl font-light text-gray-900 mb-2">
            Document Q&A
          </h1>
          <p className="text-gray-600 text-sm">
            Upload a document and ask questions about its content
          </p>
        </header>

        <main>
          {!documentId ? (
            <DocumentUpload onDocumentUploaded={handleDocumentUploaded} />
          ) : (
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
