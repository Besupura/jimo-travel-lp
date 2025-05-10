import React, { useState } from 'react';

interface StepCheckProps {
  checkpoint: {
    id: string;
    name: string;
    type: string;
    condition_data: {
      target_steps: number;
    };
  };
  onComplete: (data: any) => Promise<void>;
}

const StepCheckComponent: React.FC<StepCheckProps> = ({ checkpoint, onComplete }) => {
  const [steps, setSteps] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const { target_steps } = checkpoint.condition_data;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const stepsNumber = parseInt(steps, 10);
    if (isNaN(stepsNumber) || stepsNumber <= 0) {
      setError('Please enter a valid number of steps');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      await onComplete({ steps: stepsNumber });
    } catch (err: any) {
      console.error('Error submitting steps:', err);
      setError(err.response?.data?.message || 'Failed to verify steps. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-md">
        <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">Step Count Challenge</h3>
        <p className="text-sm text-blue-700 dark:text-blue-400">
          You need to achieve {target_steps} steps to acquire this stamp.
          For the MVP, please enter your current step count manually.
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow-sm">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="steps" className="label">Your Current Step Count</label>
            <input
              id="steps"
              type="number"
              value={steps}
              onChange={(e) => setSteps(e.target.value)}
              className="input"
              placeholder="Enter number of steps"
              min="1"
            />
            <p className="text-xs text-gray-500 mt-1">
              Target: {target_steps} steps
            </p>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting || !steps.trim()}
            className={`btn btn-primary w-full ${(isSubmitting || !steps.trim()) ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {isSubmitting ? 'Verifying Steps...' : 'Submit Step Count'}
          </button>
        </form>
      </div>

      <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-md text-sm">
        <p className="font-semibold text-yellow-800 dark:text-yellow-300">Note:</p>
        <p className="text-yellow-700 dark:text-yellow-400">
          In the future version, this will automatically sync with Google Fit or Apple Health.
        </p>
      </div>
    </div>
  );
};

export default StepCheckComponent;
