import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8030';

const FileUploader = ({ onFileChange, onUpload, file, loading }) => (
  <div className="mb-6">
    <h2 className="text-xl font-semibold mb-2">Upload File</h2>
    <Input type="file" onChange={onFileChange} accept=".txt,.md,.pdf" className="mb-2" />
    {file && <p className="text-sm text-gray-600 mb-2">File selected: {file.name}</p>}
    <Button 
      onClick={onUpload}
      disabled={!file || loading}
      className="w-full"
    >
      {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
      {loading ? 'Processing...' : 'Upload and Process'}
    </Button>
  </div>
);

FileUploader.propTypes = {
  onFileChange: PropTypes.func.isRequired,
  onUpload: PropTypes.func.isRequired,
  file: PropTypes.object,
  loading: PropTypes.bool.isRequired,
};

const UrlProcessor = ({ url, onUrlChange, onUrlSubmit, loading }) => (
  <div className="mb-6">
    <h2 className="text-xl font-semibold mb-2">Process URL</h2>
    <Input 
      type="text"
      value={url}
      onChange={onUrlChange}
      placeholder="Enter URL"
      className="mb-2"
    />
    <Button 
      onClick={onUrlSubmit}
      disabled={!url || loading}
      className="w-full"
    >
      {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
      {loading ? 'Processing...' : 'Process URL'}
    </Button>
  </div>
);

UrlProcessor.propTypes = {
  url: PropTypes.string.isRequired,
  onUrlChange: PropTypes.func.isRequired,
  onUrlSubmit: PropTypes.func.isRequired,
  loading: PropTypes.bool.isRequired,
};

const App = () => {
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUrlChange = (e) => {
    setUrl(e.target.value);
  };

  const handleFileUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Server responded with an error');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'condensed_text.txt');
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      setResult('File processed and downloaded successfully!');
    } catch (error) {
      console.error('Error:', error);
      setError('An error occurred while processing the file.');
    } finally {
      setLoading(false);
    }
  };

  const handleUrlSubmit = async () => {
    if (!url) return;

    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/process-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) throw new Error('Server responded with an error');

      const data = await response.json();
      setResult(data.condensed_text);
    } catch (error) {
      console.error('Error:', error);
      setError('An error occurred while processing the URL.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">Text Condensation Tool</h1>
      
      <FileUploader
        onFileChange={handleFileChange}
        onUpload={handleFileUpload}
        file={file}
        loading={loading}
      />

      <UrlProcessor
        url={url}
        onUrlChange={handleUrlChange}
        onUrlSubmit={handleUrlSubmit}
        loading={loading}
      />

      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {result && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-2">Result</h2>
          <pre className="bg-gray-100 p-4 rounded whitespace-pre-wrap overflow-x-auto">{result}</pre>
        </div>
      )}
    </div>
  );
};

export default App;