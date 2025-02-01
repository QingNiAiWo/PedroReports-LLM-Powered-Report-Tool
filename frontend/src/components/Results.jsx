import React, { useState } from 'react';
import { AlertCircle, Download } from 'lucide-react';
import successGif from '/assets/success.gif';  // Direct import

const Results = ({ result }) => {
  const [downloadError, setDownloadError] = useState(null);

  if (!result) return null;

  const handleDownload = async () => {
    try {
      setDownloadError(null);
      const response = await fetch('http://localhost:8000/api/v1/get-pdf');
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to download PDF');
      }
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'analysis_report.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      setDownloadError(error.message);
    }
  };

  return (
    <div className="card">
      {result.status === 'success' ? (
        <div className="success-container">
          <div className="success-icon-large">
            <img 
              src={successGif}
              alt="Success" 
              className="success-gif"
              loading="eager"
            />
          </div>
          <h3 className="success-title">Analysis Complete!</h3>
          <p className="success-message">
            Your report has been generated successfully
          </p>
          <button 
            onClick={handleDownload} 
            className="button button-primary download-button"
          >
            <Download size={20} />
            Download PDF Report
          </button>
          {downloadError && (
            <div className="error-alert mt-4">
              <AlertCircle size={20} />
              <span>{downloadError}</span>
            </div>
          )}
        </div>
      ) : (
        <div className="error-alert">
          <AlertCircle size={20} />
          <span>{result.message || 'An error occurred during analysis'}</span>
        </div>
      )}
    </div>
  );
};

export default Results;