import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ClipLoader } from 'react-spinners';

const API_URL = 'https://rkcoog4s88cwgg4kk0csgk4c.aifunnel.chat'; // Update this to your actual backend URL

function App() {
  const [file, setFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [condensedText, setCondensedText] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval;
    if (jobId && isProcessing) {
      console.log("Polling for job status with jobId:", jobId);
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`${API_URL}/status/${jobId}`);
          const result = response.data;
          console.log("Status check result:", result);
          if (result.status === 'completed') {
            setCondensedText(result.condensed_content);
            setIsProcessing(false);
            clearInterval(interval);
          } else if (result.status === 'error') {
            setIsProcessing(false);
            setError(`Error processing file: ${result.message}`);
            clearInterval(interval);
          }
        } catch (error) {
          console.error('Error checking status:', error);
          setIsProcessing(false);
          setError(`Network error while checking status: ${error.message}`);
          clearInterval(interval);
        }
      }, 5000); // Poll every 5 seconds
    }
    return () => clearInterval(interval);
  }, [jobId, isProcessing]);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsProcessing(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('Upload response:', response.data);
      setJobId(response.data.job_id);
    } catch (error) {
      console.error('Error uploading file:', error);
      setIsProcessing(false);
      setError(`Error uploading file: ${error.message}`);
    }
  };

  return (
    <div className="App">
      <h1>AI Text Condenser</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit" disabled={!file || isProcessing}>
          {isProcessing ? 'Processing...' : 'Upload and Process'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {isProcessing && (
        <div className="loading-container">
          <ClipLoader color="#36D7B7" loading={isProcessing} size={50} />
          <p>Processing your file...</p>
        </div>
      )}
      {condensedText && (
        <div>
          <h2>Condensed Text:</h2>
          <pre>{condensedText}</pre>
        </div>
      )}
    </div>
  );
}

export default App;