import React, { useState } from 'react';
import { Upload, X, CheckCircle, AlertCircle, FileVideo, Loader2 } from 'lucide-react';

interface AuditUploadModalProps {
  onClose: () => void;
  apiBase: string;
}

export function AuditUploadModal({ onClose, apiBase }: AuditUploadModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('video/')) {
      setFile(droppedFile);
      setError('');
    } else {
      setError('Please upload a valid video file (MP4, AVI, etc.)');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${apiBase}/api/audit/upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to upload video');
      }

      setSuccess('Video successfully uploaded. Retrospective audit started.');
      setTimeout(onClose, 3000);
    } catch (err: any) {
      setError(err.message || 'An error occurred during upload.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="bg-[#111827] border border-slate-700 rounded-lg shadow-2xl w-full max-w-lg overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-slate-700 bg-slate-800/50">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Upload className="w-5 h-5 text-cyan-400" />
            Batch Video Upload
          </h2>
          <button onClick={onClose} className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          <p className="text-sm text-slate-400 mb-6">
            Upload raw surveillance footage or drone recordings for offline retrospective threat auditing. 
            The video will be processed by the full AI pipeline at maximum speed.
          </p>

          {!success ? (
            <>
              <div 
                className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center transition-colors cursor-pointer
                  ${file ? 'border-cyan-500 bg-cyan-900/20' : 'border-slate-600 hover:border-cyan-400 hover:bg-slate-800'}`}
                onDragOver={e => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-upload')?.click()}
              >
                <input 
                  type="file" 
                  id="file-upload" 
                  className="hidden" 
                  accept="video/mp4,video/x-m4v,video/*"
                  onChange={e => {
                    const f = e.target.files?.[0];
                    if (f) { setFile(f); setError(''); }
                  }}
                />
                
                {file ? (
                  <>
                    <FileVideo className="w-12 h-12 text-cyan-400 mb-3" />
                    <p className="text-white font-medium text-center">{file.name}</p>
                    <p className="text-slate-400 text-sm mt-1">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </>
                ) : (
                  <>
                    <Upload className="w-12 h-12 text-slate-500 mb-3" />
                    <p className="text-white font-medium">Click or drag video file here</p>
                    <p className="text-slate-400 text-sm mt-1">Supports MP4, AVI, MKV (Max 500MB)</p>
                  </>
                )}
              </div>

              {error && (
                <div className="mt-4 p-3 bg-red-900/30 border border-red-500/50 rounded flex items-start gap-2 text-red-200 text-sm">
                  <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                  <p>{error}</p>
                </div>
              )}

              <div className="mt-6 flex justify-end gap-3">
                <button 
                  onClick={onClose}
                  className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
                  disabled={uploading}
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpload}
                  disabled={!file || uploading}
                  className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {uploading ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /> Processing...</>
                  ) : 'Start Audit'}
                </button>
              </div>
            </>
          ) : (
            <div className="py-8 flex flex-col items-center text-center">
              <CheckCircle className="w-16 h-16 text-emerald-500 mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Audit Initiated</h3>
              <p className="text-slate-400 text-sm">
                The video is now being processed in the background. 
                <br />Threats will appear in the Intelligence Panel marked as <b>IMPORTED</b>.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
