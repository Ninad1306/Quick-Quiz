import React, { useState } from "react";
import Modal from "../Utils/Modal"; // Assuming this is your path

const PublishQuiz = ({ show, onClose, onSubmit, loading }) => {
  // 1. State only holds the "raw" local date string
  const [publishForm, setPublishForm] = useState({
    start_time: "",
  });

  // 2. Helper to handle the final submission
  const handlePublishClick = () => {
    // Create the data specifically for the backend here
    const payload = {
      ...publishForm,
      // We append the UTC 'Z' and seconds ONLY when sending to parent/backend
      start_time: publishForm.start_time ? publishForm.start_time + ":00Z" : ""
    };
    
    onSubmit(payload);
  };

  return (
    <Modal show={show} onClose={onClose} title="Publish Quiz">
      {/* Note: Removed the extra <div className="bg-white..."> wrapper 
         because your 'Modal' component likely already has the white box.
         If your Modal component is just an overlay, keep the div.
      */}
      <div className="w-full"> 
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            Start Time (UTC)
          </label>
          <input
            type="datetime-local"
            // 3. Value is directly bound to state (YYYY-MM-DDThh:mm)
            value={publishForm.start_time}
            onChange={(e) =>
              setPublishForm({
                ...publishForm,
                // 4. Just save the raw input value. Don't add 'Z' yet.
                start_time: e.target.value, 
              })
            }
            className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          <p className="text-xs text-gray-500 mt-1">
            Select when students can start attempting the quiz
          </p>
        </div>
        
        <div className="flex gap-2 mt-6">
          <button
            // 5. Call the local handler instead of binding directly
            onClick={handlePublishClick}
            disabled={loading || !publishForm.start_time}
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Publishing..." : "Publish"}
          </button>
          
          <button
            // 6. Fixed: Use 'onClose' prop, not 'setShowPublishModal' which is undefined here
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-700 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default PublishQuiz;