import React, { useState } from "react";
import Modal from "../Utils/Modal";
import { Trash2 } from "lucide-react";
import { API_BASE_URL } from "../../constants";
import axios from "axios";

const DeleteQuestions = ({ show, onClose, questions, quizId, onUpdate }) => {
  const [selectedQuestions, setSelectedQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleToggleQuestion = (questionId) => {
    setSelectedQuestions((prev) =>
      prev.includes(questionId)
        ? prev.filter((id) => id !== questionId)
        : [...prev, questionId]
    );
  };

  const handleSelectAll = () => {
    if (selectedQuestions.length === questions.length) {
      setSelectedQuestions([]);
    } else {
      setSelectedQuestions(questions.map((q) => q.question_id));
    }
  };

  const handleDelete = async () => {
    if (selectedQuestions.length === 0) {
      setError("Please select at least one question to delete");
      return;
    }

    if (
      !confirm(
        `Are you sure you want to delete ${selectedQuestions.length} question(s)?`
      )
    ) {
      return;
    }

    setError("");
    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      await axios.post(
        `${API_BASE_URL}/teacher/delete_questions/${quizId}`,
        { question_ids: selectedQuestions },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      onUpdate();
      onClose();
      setSelectedQuestions([]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onClose={onClose} title="Delete Questions">
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      <div className="mb-4 flex items-center justify-between">
        <span className="text-sm text-gray-600">
          {selectedQuestions.length} of {questions.length} selected
        </span>
        <button
          onClick={handleSelectAll}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          {selectedQuestions.length === questions.length
            ? "Deselect All"
            : "Select All"}
        </button>
      </div>

      <div className="max-h-96 overflow-y-auto space-y-2">
        {questions.map((question) => (
          <div
            key={question.question_id}
            className={`p-4 border rounded-lg cursor-pointer transition ${
              selectedQuestions.includes(question.question_id)
                ? "border-red-500 bg-red-50"
                : "border-gray-200 hover:border-gray-300"
            }`}
            onClick={() => handleToggleQuestion(question.question_id)}
          >
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                checked={selectedQuestions.includes(question.question_id)}
                onChange={() => handleToggleQuestion(question.question_id)}
                className="mt-1"
              />
              <div className="flex-1">
                <p className="font-medium text-gray-800">
                  {question.question_text}
                </p>
                <div className="flex gap-2 mt-2 text-xs">
                  <span className="px-2 py-1 bg-gray-100 rounded">
                    {question.question_type.toUpperCase()}
                  </span>
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                    {question.marks} marks
                  </span>
                  <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded">
                    {question.difficulty_level}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-3 mt-6">
        <button
          onClick={handleDelete}
          disabled={loading || selectedQuestions.length === 0}
          className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 disabled:bg-gray-400 transition flex items-center justify-center gap-2"
        >
          <Trash2 size={16} />
          {loading
            ? "Deleting..."
            : `Delete ${selectedQuestions.length} Question(s)`}
        </button>
        <button
          onClick={onClose}
          className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300 transition"
        >
          Cancel
        </button>
      </div>
    </Modal>
  );
};

export default DeleteQuestions;
