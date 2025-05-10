import React, { useState } from 'react';

interface QuizProps {
  checkpoint: {
    id: string;
    name: string;
    type: string;
    condition_data: {
      question: string;
      options?: string[];
      correct_answer: string;
    };
  };
  onComplete: (data: any) => Promise<void>;
}

const QuizComponent: React.FC<QuizProps> = ({ checkpoint, onComplete }) => {
  const [answer, setAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const { question, options, correct_answer } = checkpoint.condition_data;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!answer.trim()) {
      setError('Please provide an answer');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      await onComplete({ answer });
    } catch (err: any) {
      console.error('Error submitting answer:', err);
      setError(err.response?.data?.message || 'Incorrect answer. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-md">
        <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">Quiz Challenge</h3>
        <p className="text-sm text-blue-700 dark:text-blue-400">
          Answer the question correctly to acquire this stamp.
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow-sm">
        <h3 className="font-semibold text-lg mb-3">{question}</h3>
        
        <form onSubmit={handleSubmit}>
          {options && options.length > 0 ? (
            <div className="space-y-2 mb-4">
              {options.map((option, index) => (
                <label key={index} className="flex items-start space-x-2 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
                  <input
                    type="radio"
                    name="quiz-answer"
                    value={option}
                    checked={answer === option}
                    onChange={() => setAnswer(option)}
                    className="mt-1"
                  />
                  <span>{option}</span>
                </label>
              ))}
            </div>
          ) : (
            <div className="mb-4">
              <label htmlFor="answer" className="label">Your Answer</label>
              <input
                id="answer"
                type="text"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                className="input"
                placeholder="Type your answer here"
              />
            </div>
          )}

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting || !answer.trim()}
            className={`btn btn-primary w-full ${(isSubmitting || !answer.trim()) ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {isSubmitting ? 'Checking Answer...' : 'Submit Answer'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default QuizComponent;
