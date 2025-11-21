import React, { useState } from "react";
import { Clock } from "lucide-react";
import Modal from "../Utils/Modal";
import axios from "axios";
import { API_BASE_URL } from "../../constants";

const ModifyDuration = ({ show, onClose, quizId, currentDuration }) => {
  const [extraTime, setExtraTime] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setError("");
    setLoading(true);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/teacher/modify_quiz_duration/${quizId}`,
        { extra_time: parseInt(extraTime) },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );

      const data = response.data;

      if (response.statusText !== "OK") {
        throw new Error(data.error || "Failed to modify duration");
      }

      alert("Duration modified successfully!");
      onClose();
      setExtraTime("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onClose={onClose} title="Modify Quiz Duration">
      <div>
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-700">
              Current Duration:{" "}
              <span className="font-bold">{currentDuration} minutes</span>
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Time (minutes) *
            </label>
            <input
              type="number"
              value={extraTime}
              onChange={(e) => setExtraTime(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., 15"
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              Enter positive value to add time, negative to reduce
            </p>
          </div>

          {extraTime && (
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-700">
                New Duration:{" "}
                <span className="font-bold">
                  {parseInt(currentDuration) + parseInt(extraTime)} minutes
                </span>
              </p>
            </div>
          )}
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={handleSubmit}
            disabled={loading || !extraTime}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition flex items-center justify-center gap-2"
          >
            <Clock size={16} />
            {loading ? "Updating..." : "Update Duration"}
          </button>
          <button
            onClick={onClose}
            className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300 transition"
          >
            Cancel
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default ModifyDuration;
