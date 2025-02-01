import React, { useState, useEffect } from 'react';
import { Moon, Sun } from 'lucide-react';
import FileUpload from './components/FileUpload';
import Questions from './components/Questions';
import Results from './components/Results';
import ConfirmationDialog from './components/ConfirmationDialog';
import './App.css';

const ThemeToggle = ({ theme, onToggle }) => (
  <button className="theme-toggle" onClick={onToggle}>
    {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
  </button>
);

const App = () => {
  // All state declarations
  const [file, setFile] = useState(null);
  const [questions, setQuestions] = useState(['']);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [reportTitle, setReportTitle] = useState('');
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [theme, setTheme] = useState(() => 
    localStorage.getItem('theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
  );

  // Theme effect
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  // File handling functions
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && (selectedFile.name.endsWith('.csv') || selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.xls'))) {
      setFile(selectedFile);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.name.endsWith('.csv') || droppedFile.name.endsWith('.xlsx') || droppedFile.name.endsWith('.xls'))) {
      setFile(droppedFile);
    }
  };

  // Question handling
  const handleQuestionChange = (index, value) => {
    const newQuestions = [...questions];
    newQuestions[index] = value;
    setQuestions(newQuestions);
  };

  // Report generation functions
  const generateReport = async () => {
    const finalReportTitle = reportTitle.trim() || 'Data Analysis Report';
    
    setResult(null);
    setLoading(true);
    setShowConfirmDialog(false);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch('http://localhost:8000/api/v1/upload-dataset', {
        method: 'POST',
        body: formData,
      });

      const uploadData = await uploadResponse.json();
      if (uploadData.status !== 'success') {
        throw new Error(uploadData.message || 'Upload failed');
      }

      const analysisResponse = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          questions: questions.filter(q => q.trim()),
          reportTitle: finalReportTitle
        }),
      });

      const analysisData = await analysisResponse.json();
      setResult(analysisData);
    } catch (error) {
      console.error('Error:', error);
      setResult({ status: 'error', message: error.message });
    }
    setLoading(false);
  };

  const handleSubmit = () => {
    if (!file) {
      setResult({ status: 'error', message: 'Please select a file' });
      return;
    }

    // If there's already a successful result, show confirmation dialog
    if (result && result.status === 'success') {
      setShowConfirmDialog(true);
      return;
    }

    // Otherwise proceed with report generation
    generateReport();
  };

  return (
    <div className="app-container">
      <ThemeToggle theme={theme} onToggle={toggleTheme} />
      <div className="content-wrapper">
        <div className="header">
          <h1 className="title">PedroReports - Your Pawsome Reporter</h1>
          <p className="subtitle">Upload your dataset and get comprehensive analysis reports</p>
        </div>

        <div className="main-content">
          <FileUpload
            file={file}
            onFileChange={handleFileChange}
            dragActive={dragActive}
            handleDrag={handleDrag}
            handleDrop={handleDrop}
          />
          
          <div className="card">
            <div className="report-title-section">
              <label htmlFor="reportTitle" className="report-title-label">
                Please enter a title for your analysis report
              </label>
              <input
                id="reportTitle"
                type="text"
                value={reportTitle}
                onChange={(e) => setReportTitle(e.target.value)}
                placeholder="Enter Report Title"
                className="input-field"
              />
              <p className="report-title-hint">
                Leave blank to use default title: "Data Analysis Report"
              </p>
            </div>
          </div>

          <Questions
            questions={questions}
            onQuestionChange={handleQuestionChange}
            onAddQuestion={() => setQuestions([...questions, ''])}
            onRemoveQuestion={(index) => {
              const newQuestions = questions.filter((_, i) => i !== index);
              setQuestions(newQuestions);
            }}
          />

          <button
            onClick={handleSubmit}
            disabled={!file || loading || questions[0] === ''}
            className="button button-primary"
            style={{ width: '100%', padding: '1rem' }}
          >
            {loading ? 'Generating Report...' : 'Generate Analysis Report'}
          </button>

          {result && <Results result={result} />}
        </div>
      </div>

      {/* Confirmation Dialog */}
      <ConfirmationDialog 
        open={showConfirmDialog}
        onOpenChange={setShowConfirmDialog}
        onContinue={generateReport}
      />
    </div>
  );
};

export default App;