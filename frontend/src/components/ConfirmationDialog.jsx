import React from 'react';
import { AlertCircle } from 'lucide-react';

const ConfirmationDialog = ({ open, onOpenChange, onContinue }) => {
  if (!open) return null;

  return (
    <div className="dialog-overlay">
      {/* Backdrop */}
      <div 
        className="dialog-backdrop"
        onClick={() => onOpenChange(false)}
      />
      
      {/* Dialog */}
      <div className="card dialog-content">
        <div className="error-alert">
          <AlertCircle size={20} />
          <span className="title">Warning</span>
        </div>
        
        <p className="dialog-message">
          Generating a new report will prevent you from downloading the previous report. 
          Are you sure you want to continue?
        </p>
        
        <div className="dialog-buttons">
          <button
            onClick={() => onOpenChange(false)}
            className="button button-outline"
          >
            Cancel
          </button>
          <button
            onClick={onContinue}
            className="button button-primary"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationDialog;