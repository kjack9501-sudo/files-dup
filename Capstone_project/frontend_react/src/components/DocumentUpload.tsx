import { useState } from 'react';
import { Upload, FileText, Loader2 } from 'lucide-react';
import { apiService } from '../services/api';

interface DocumentUploadProps {
  onDocumentUploaded: (id: string, name: string) => void;
}

export default function DocumentUpload({ onDocumentUploaded }: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const acceptedTypes = ['.pdf', '.txt', '.docx'];
  const acceptedMimeTypes = [
    'application/pdf',
    'text/plain',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ];

  const handleFile = async (file: File) => {
    setError(null);

    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedTypes.includes(fileExtension)) {
      setError('Please upload a PDF, TXT, or DOCX file');
      return;
    }

    setUploading(true);

    try {
      const result = await apiService.uploadDocument(file);
      
      if (result.success && result.documentId && result.filename) {
        onDocumentUploaded(result.documentId, result.filename);
      } else {
        setError(result.error || 'Failed to upload document. Please try again.');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to upload document. Please try again.');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
      <div
        className={`relative border-2 border-dashed rounded-lg p-12 transition-colors ${
          dragActive
            ? 'border-gray-400 bg-gray-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept={acceptedMimeTypes.join(',')}
          onChange={handleFileInput}
          disabled={uploading}
        />

        <label
          htmlFor="file-upload"
          className="flex flex-col items-center cursor-pointer"
        >
          {uploading ? (
            <>
              <Loader2 className="w-12 h-12 text-gray-400 animate-spin mb-4" />
              <p className="text-sm text-gray-600">Processing document...</p>
            </>
          ) : (
            <>
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Upload className="w-8 h-8 text-gray-500" />
              </div>
              <p className="text-base font-medium text-gray-900 mb-1">
                Upload a document
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Drag and drop or click to browse
              </p>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <FileText className="w-4 h-4" />
                <span>PDF, TXT, DOCX</span>
              </div>
            </>
          )}
        </label>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-800">
          {error}
        </div>
      )}
    </div>
  );
}
