import React from 'react';
import { Upload, FileText } from 'lucide-react';

const FileUpload = ({ file, onFileChange, dragActive, handleDrag, handleDrop }) => (
  <div className="card">
    <div className="card-title">
      <FileText className="text-blue-500" />
      Dataset Upload
    </div>
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      className={`upload-area ${dragActive ? 'active' : ''}`}
    >
      <input
        type="file"
        onChange={onFileChange}
        style={{ display: 'none' }}
        id="fileInput"
        accept=".csv"
      />
      <label htmlFor="fileInput">
        <Upload className="h-8 w-8 text-blue-500" />
        <p className="upload-text">
          {file ? file.name : 'Drop your file here or click to upload'}
        </p>
        <p className="upload-subtitle">
          Supports Only CSV Files
        </p>
      </label>
    </div>
  </div>
);

export default FileUpload;

const ReportTitleInput = () => (
  <div className="card">
    <div className="card-title">
      Report Title
    </div>
    <input
      value={reportTitle}
      onChange={(e) => setReportTitle(e.target.value)}
      placeholder="Enter report title"
      className="input-field"
    />
  </div>
);