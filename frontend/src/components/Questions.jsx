import React from 'react';
import { Plus, Minus } from 'lucide-react';

const Questions = ({ questions, onQuestionChange, onAddQuestion, onRemoveQuestion }) => {
  return (
    <div className="card">
      <div className="card-title">Analysis Questions</div>
      <div className="questions-wrapper">
        {questions.map((question, index) => (
          <div key={index} className="question-container">
            <input
              value={question}
              onChange={(e) => onQuestionChange(index, e.target.value)}
              placeholder="What would you like to analyze?"
              className="input-field"
            />
            {questions.length > 1 && (
              <button
                onClick={() => onRemoveQuestion(index)}
                className="button button-outline"
              >
                <Minus size={16} />
              </button>
            )}
          </div>
        ))}
        <button
          onClick={onAddQuestion}
          className="button button-outline"
        >
          <Plus size={16} />
          Add Question
        </button>
      </div>
    </div>
  );
};

export default Questions;