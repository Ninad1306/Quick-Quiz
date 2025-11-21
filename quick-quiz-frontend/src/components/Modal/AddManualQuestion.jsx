import React, { useState } from "react";
import { X, Plus, PlusCircle } from "lucide-react";
import Modal from "../Utils/Modal";
import axios from "axios";
import { API_BASE_URL } from "../../constants";

const AddManualQuestion = ({ show, onClose, quizId, onUpdate }) => {
  const [questionData, setQuestionData] = useState({
    question_type: "mcq",
    question_text: "",
    options: [
      { id: "A", text: "" },
      { id: "B", text: "" },
    ],
    correct_answer: "",
    tags: "",
    marks: "",
    difficulty_level: "easy",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const addOption = () => {
    const nextId = String.fromCharCode(65 + questionData.options.length);
    setQuestionData((prev) => ({
      ...prev,
      options: [...prev.options, { id: nextId, text: "" }],
    }));
  };

  const removeOption = (index) => {
    if (questionData.options.length <= 2) return;
    setQuestionData((prev) => ({
      ...prev,
      options: prev.options.filter((_, i) => i !== index),
    }));
  };

  const updateOption = (index, text) => {
    setQuestionData((prev) => ({
      ...prev,
      options: prev.options.map((opt, i) =>
        i === index ? { ...opt, text } : opt
      ),
    }));
  };

  const handleSubmit = async () => {
    setError("");
    setLoading(true);

    try {
      const token = localStorage.getItem("token");

      const payload = {
        question_type: questionData.question_type,
        question_text: questionData.question_text,
        difficulty_level: questionData.difficulty_level,
        marks: parseFloat(questionData.marks),
        tags: questionData.tags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
      };

      if (questionData.question_type === "mcq") {
        payload.options = questionData.options;
        payload.correct_answer = questionData.correct_answer;
      } else if (questionData.question_type === "msq") {
        payload.options = questionData.options;
        payload.correct_answer = questionData.correct_answer
          .split(",")
          .map((a) => a.trim())
          .filter(Boolean);
      } else if (questionData.question_type === "nat") {
        payload.options = null;
        payload.correct_answer = parseInt(questionData.correct_answer);
      }

      const response = await axios.post(
        `${API_BASE_URL}/teacher/add_quiz_questions/${quizId}`,
        [payload],
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = response.data;

      if (response.status !== 201) {
        throw new Error(data.error || "Failed to add question");
      }

      onUpdate();
      onClose();
      setQuestionData({
        question_type: "mcq",
        question_text: "",
        options: [
          { id: "A", text: "" },
          { id: "B", text: "" },
        ],
        correct_answer: "",
        tags: "",
        marks: "",
        difficulty_level: "easy",
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const isFormValid = () => {
    if (
      !questionData.question_text ||
      !questionData.marks ||
      !questionData.tags
    )
      return false;
    if (
      questionData.question_type === "mcq" ||
      questionData.question_type === "msq"
    ) {
      return (
        questionData.options.every((opt) => opt.text.trim()) &&
        questionData.correct_answer
      );
    }
    if (questionData.question_type === "nat") {
      return questionData.correct_answer !== "";
    }
    return false;
  };

  return (
    <Modal show={show} onClose={onClose} title="Add Question Manually">
      <div>
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Question Type *
              </label>
              <select
                value={questionData.question_type}
                onChange={(e) =>
                  setQuestionData({
                    ...questionData,
                    question_type: e.target.value,
                    correct_answer: "",
                  })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="mcq">Multiple Choice (Single)</option>
                <option value="msq">Multiple Select</option>
                <option value="nat">Numerical Answer</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Difficulty Level *
              </label>
              <select
                value={questionData.difficulty_level}
                onChange={(e) =>
                  setQuestionData({
                    ...questionData,
                    difficulty_level: e.target.value,
                  })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Question Text *
            </label>
            <textarea
              value={questionData.question_text}
              onChange={(e) =>
                setQuestionData({
                  ...questionData,
                  question_text: e.target.value,
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows="3"
            />
          </div>

          {(questionData.question_type === "mcq" ||
            questionData.question_type === "msq") && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Options *
              </label>
              {questionData.options.map((option, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <span className="px-3 py-2 bg-gray-100 rounded-lg font-medium">
                    {option.id}
                  </span>
                  <input
                    type="text"
                    value={option.text}
                    onChange={(e) => updateOption(index, e.target.value)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder={`Option ${option.id}`}
                  />
                  {questionData.options.length > 2 && (
                    <button
                      onClick={() => removeOption(index)}
                      className="px-3 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200"
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={addOption}
                className="mt-2 text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                <Plus size={16} /> Add Option
              </button>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Correct Answer *
            </label>
            <input
              type="text"
              value={questionData.correct_answer}
              onChange={(e) =>
                setQuestionData({
                  ...questionData,
                  correct_answer: e.target.value,
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder={
                questionData.question_type === "mcq"
                  ? "e.g., A"
                  : questionData.question_type === "msq"
                  ? "e.g., A, B, C"
                  : "e.g., 42"
              }
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags (comma-separated) *
              </label>
              <input
                type="text"
                value={questionData.tags}
                onChange={(e) =>
                  setQuestionData({ ...questionData, tags: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., algebra, equations"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Marks *
              </label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                value={questionData.marks}
                onChange={(e) =>
                  setQuestionData({ ...questionData, marks: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={handleSubmit}
            disabled={loading || !isFormValid()}
            className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition flex items-center justify-center gap-2"
          >
            <PlusCircle size={16} />
            {loading ? "Adding..." : "Add Question"}
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

export default AddManualQuestion;
