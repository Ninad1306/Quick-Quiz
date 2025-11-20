import React, { useState } from "react";
import Modal from "../Utils/Modal";

const PublishQuiz = ({ show, onClose, onSubmit, loading }) => {
  const [publishForm, setPublishForm] = useState({
    start_time: "",
  });

  const handlePublishClick = () => {
    const payload = {
      ...publishForm,
      start_time: publishForm.start_time,
    };

    onSubmit(payload);
  };

  return (
    <Modal show={show} onClose={onClose} title="Publish Quiz">
      <div className="w-full">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            Start Time (UTC)
          </label>
          <input
            type="datetime-local"
            value={publishForm.start_time}
            onChange={(e) =>
              setPublishForm({
                ...publishForm,
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
            onClick={handlePublishClick}
            disabled={loading || !publishForm.start_time}
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Publishing..." : "Publish"}
          </button>

          <button
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
