import React, { useState, useRef, useEffect } from 'react';
import { Html5Qrcode } from 'html5-qrcode';

interface QRScanProps {
  checkpoint: {
    id: string;
    name: string;
    type: string;
    condition_data: {
      expected_code: string;
    };
  };
  onComplete: (data: any) => Promise<void>;
}

const QRScanComponent: React.FC<QRScanProps> = ({ checkpoint, onComplete }) => {
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState('');
  const [scannedCode, setScannedCode] = useState('');
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const scannerContainerId = 'qr-reader';

  useEffect(() => {
    return () => {
      if (scannerRef.current) {
        scannerRef.current.stop().catch(err => {
          console.error('Error stopping scanner:', err);
        });
      }
    };
  }, []);

  const startScanner = async () => {
    setError('');
    setIsScanning(true);

    try {
      const html5QrCode = new Html5Qrcode(scannerContainerId);
      scannerRef.current = html5QrCode;

      const qrCodeSuccessCallback = async (decodedText: string) => {
        setScannedCode(decodedText);
        
        if (scannerRef.current) {
          await scannerRef.current.stop();
        }
        
        try {
          await onComplete({ qr_code: decodedText });
        } catch (err) {
          console.error('Error submitting QR code:', err);
          setError('Failed to verify QR code. Please try again.');
        }
      };

      const config = { fps: 10, qrbox: { width: 250, height: 250 } };

      await html5QrCode.start(
        { facingMode: "environment" },
        config,
        qrCodeSuccessCallback,
        (errorMessage) => {
          console.log('QR scan error:', errorMessage);
        }
      );
    } catch (err: any) {
      console.error('Error starting QR scanner:', err);
      setError(err.message || 'Failed to start camera. Please check permissions and try again.');
      setIsScanning(false);
    }
  };

  const stopScanner = async () => {
    if (scannerRef.current) {
      try {
        await scannerRef.current.stop();
        setIsScanning(false);
      } catch (err) {
        console.error('Error stopping scanner:', err);
      }
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-md">
        <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">QR Code Scanning Required</h3>
        <p className="text-sm text-blue-700 dark:text-blue-400">
          Scan the QR code at this checkpoint to acquire the stamp.
          Please allow camera access when prompted.
        </p>
      </div>

      <div id={scannerContainerId} className={`w-full ${isScanning ? 'h-64' : 'h-0'} overflow-hidden rounded-md`}></div>

      {scannedCode && (
        <div className="bg-green-100 dark:bg-green-900/20 p-3 rounded-md">
          <p className="font-semibold text-green-800 dark:text-green-300">QR Code scanned successfully!</p>
          <p className="text-sm text-green-700 dark:text-green-400">Verifying code...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p className="font-semibold">Error:</p>
          <p>{error}</p>
          {error.includes('permission') && (
            <p className="text-sm mt-2">
              Please enable camera access in your browser settings and try again.
            </p>
          )}
        </div>
      )}

      {!isScanning && !scannedCode ? (
        <button
          onClick={startScanner}
          className="btn btn-primary w-full"
        >
          Start Camera and Scan QR Code
        </button>
      ) : isScanning && !scannedCode ? (
        <button
          onClick={stopScanner}
          className="btn btn-outline w-full"
        >
          Cancel Scanning
        </button>
      ) : null}
    </div>
  );
};

export default QRScanComponent;
