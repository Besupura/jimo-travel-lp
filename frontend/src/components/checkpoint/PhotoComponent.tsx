import React, { useState, useRef } from 'react';

interface PhotoProps {
  checkpoint: {
    id: string;
    name: string;
    type: string;
    condition_data: {
      description?: string;
    };
  };
  onComplete: (data: any) => Promise<void>;
}

const PhotoComponent: React.FC<PhotoProps> = ({ checkpoint, onComplete }) => {
  const [photo, setPhoto] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      
      if (file.size > 5 * 1024 * 1024) {
        setError('File size exceeds 5MB limit. Please choose a smaller image.');
        return;
      }
      
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file.');
        return;
      }
      
      setPhoto(file);
      setPreview(URL.createObjectURL(file));
      setError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!photo) {
      setError('Please select a photo to upload');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('photo', photo);
      
      await onComplete({ photo: formData });
    } catch (err: any) {
      console.error('Error submitting photo:', err);
      setError(err.response?.data?.message || 'Failed to upload photo. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-md">
        <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">Photo Submission Required</h3>
        <p className="text-sm text-blue-700 dark:text-blue-400">
          Take a photo at this checkpoint and submit it to acquire the stamp.
          {checkpoint.condition_data.description && (
            <span className="block mt-1">
              {checkpoint.condition_data.description}
            </span>
          )}
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow-sm">
        <form onSubmit={handleSubmit}>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/*"
            capture="environment"
            className="hidden"
          />
          
          {preview ? (
            <div className="mb-4">
              <div className="relative">
                <img 
                  src={preview} 
                  alt="Preview" 
                  className="w-full h-auto rounded-md max-h-64 object-contain bg-gray-100 dark:bg-gray-700"
                />
                <button
                  type="button"
                  onClick={triggerFileInput}
                  className="absolute bottom-2 right-2 bg-white dark:bg-gray-800 p-2 rounded-full shadow-md"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600 dark:text-gray-300" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Click the edit icon to change the photo
              </p>
            </div>
          ) : (
            <div className="mb-4">
              <button
                type="button"
                onClick={triggerFileInput}
                className="w-full h-48 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-md flex flex-col items-center justify-center text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>Take Photo or Select from Gallery</span>
              </button>
            </div>
          )}

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting || !photo}
            className={`btn btn-primary w-full ${(isSubmitting || !photo) ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {isSubmitting ? 'Uploading Photo...' : 'Submit Photo'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default PhotoComponent;
