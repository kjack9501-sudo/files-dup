import { useState } from 'react';
import { Send, FileText, X, Loader2 } from 'lucide-react';

interface QuestionAnswerProps {
  documentId: string;
  documentName: string;
  onReset: () => void;
}

interface QAPair {
  question: string;
  answer: string;
  timestamp: number;
}

export default function QuestionAnswer({
  documentId,
  documentName,
  onReset,
}: QuestionAnswerProps) {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<QAPair[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!question.trim() || loading) return;

    const currentQuestion = question.trim();
    setQuestion('');
    setLoading(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 1500));

      const mockAnswer = `Based on the document "${documentName}", here is the answer to your question: "${currentQuestion}". This is a simulated response that would normally come from your backend processing system after analyzing the document content.`;

      setHistory(prev => [
        ...prev,
        {
          question: currentQuestion,
          answer: mockAnswer,
          timestamp: Date.now(),
        },
      ]);
    } catch (err) {
      console.error('Error getting answer:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gray-100 rounded flex items-center justify-center">
              <FileText className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">{documentName}</p>
              <p className="text-xs text-gray-500">Document ready for questions</p>
            </div>
          </div>
          <button
            onClick={onReset}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
            title="Upload new document"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {history.length > 0 && (
          <div className="p-6 space-y-6 max-h-[500px] overflow-y-auto">
            {history.map((qa, index) => (
              <div key={qa.timestamp} className="space-y-3">
                {index > 0 && <div className="border-t border-gray-100 -mx-6 mb-6" />}

                <div className="space-y-1">
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Question
                  </p>
                  <p className="text-sm text-gray-900">{qa.question}</p>
                </div>

                <div className="space-y-1">
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Answer
                  </p>
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {qa.answer}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className={`p-6 ${history.length > 0 ? 'border-t border-gray-200' : ''}`}>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
                Ask a question
              </label>
              <textarea
                id="question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="What would you like to know about this document?"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent text-sm"
                rows={3}
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={!question.trim() || loading}
              className="w-full sm:w-auto px-6 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Ask Question</span>
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
