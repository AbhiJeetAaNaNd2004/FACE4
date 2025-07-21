import React from 'react';
import { Camera } from '../../types';
import { Button } from '../ui/Button';

interface CameraSwitcherProps {
  cameras: Camera[];
  selectedCameras: number[];
  onCameraToggle: (cameraId: number) => void;
  maxSelection?: number;
  className?: string;
}

export const CameraSwitcher: React.FC<CameraSwitcherProps> = ({
  cameras,
  selectedCameras,
  onCameraToggle,
  maxSelection = 4,
  className = ""
}) => {
  const activeCameras = cameras.filter(camera => camera.is_active);

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Camera Selection</h3>
        <span className="text-sm text-gray-500">
          {selectedCameras.length}/{maxSelection} selected
        </span>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {activeCameras.map(camera => {
          const isSelected = selectedCameras.includes(camera.id);
          const canSelect = isSelected || selectedCameras.length < maxSelection;
          
          return (
            <Button
              key={camera.id}
              variant={isSelected ? "default" : "outline"}
              size="sm"
              onClick={() => onCameraToggle(camera.id)}
              disabled={!canSelect}
              className={`p-3 h-auto flex-col text-center ${
                isSelected 
                  ? 'bg-primary-600 text-white border-primary-600' 
                  : canSelect 
                    ? 'hover:bg-gray-50' 
                    : 'opacity-50 cursor-not-allowed'
              }`}
            >
              <div className="text-xs font-medium truncate w-full">
                {camera.name}
              </div>
              <div className="text-xs opacity-80 mt-1">
                Camera {camera.id}
              </div>
              <div className={`w-2 h-2 rounded-full mt-2 ${
                camera.is_active ? 'bg-green-400' : 'bg-red-400'
              }`} />
            </Button>
          );
        })}
      </div>

      {activeCameras.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">📹</div>
          <p>No active cameras available</p>
          <p className="text-sm mt-1">Configure cameras in Camera Management</p>
        </div>
      )}

      {selectedCameras.length >= maxSelection && (
        <div className="text-sm text-amber-600 bg-amber-50 border border-amber-200 rounded-md p-3">
          Maximum number of cameras selected. Deselect a camera to choose another.
        </div>
      )}
    </div>
  );
};