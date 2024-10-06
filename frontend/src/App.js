import React, { useState } from 'react';
import useSWR from 'swr';

const fetcher = (url, options) => fetch(url, options).then((res) => res.json());

function App() {
  const [url, setUrl] = useState('');
  const [file, setFile] = useState(null);

  const { data, error } = useSWR(
    url ? [`http://localhost:8030/process-url`, url] : null,
    ([url, body]) =>
      fetcher(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: body }),
      })
  );

  const handleUrlSubmit = (e) => {
    e.preventDefault();
    // The SWR hook will automatically fetch when the URL changes
  };

  const handleFileSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8030/upload', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      console.log(result);
      // Handle the result as needed
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl"></div>
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div className="max-w-md mx-auto">
            <div>
              <h1 className="text-2xl font-semibold">AI Text Condenser</h1>
            </div>
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <form onSubmit={handleUrlSubmit} className="space-y-4">
                  <div>
                    <label htmlFor="url" className="block text-sm font-medium text-gray-700">
                      Enter URL
                    </label>
                    <input
                      type="url"
                      id="url"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Process URL
                  </button>
                </form>

                <form onSubmit={handleFileSubmit} className="space-y-4">
                  <div>
                    <label htmlFor="file" className="block text-sm font-medium text-gray-700">
                      Upload File
                    </label>
                    <input
                      type="file"
                      id="file"
                      className="mt-1 block w-full"
                      onChange={(e) => setFile(e.target.files[0])}
                      accept=".txt,.pdf,.doc,.docx"
                    />
                  </div>
                  <button
                    type="submit"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Upload and Process
                  </button>
                </form>
              </div>
            </div>

            {error && (
              <div className="mt-4 text-red-600">
                Error: {error.message}
              </div>
            )}

            {data && (
              <div className="mt-4">
                <h2 className="text-xl font-semibold">Condensed Text:</h2>
                <p className="mt-2 text-gray-600">{data.condensed_text}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;