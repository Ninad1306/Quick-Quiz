import React, { useState, useEffect } from "react";
import { Clock, AlertCircle, CheckCircle, Calendar } from "lucide-react";
import { API_BASE_URL } from "../../constants";

const getAuthHeaders = () => ({
  Authorization: `Bearer ${localStorage.getItem("token")}`,
  "Content-Type": "application/json",
});

const TeacherQuizManagement = ({ quiz, onBack }) => {
  const [quizData, setQuizData] = useState(quiz);
  const [questions, setQuestions] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    title: quiz.title,
    description: quiz.description,
    duration_minutes: quiz.duration_minutes,
    passing_marks: quiz.passing_marks,
  });
  const [publishForm, setPublishForm] = useState({
    start_time: "",
  });
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [showModifyModal, setShowModifyModal] = useState(false);
  const [extraTime, setExtraTime] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  useEffect(() => {
    fetchQuestions();
  }, [quiz.test_id]);

  const fetchQuestions = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/teacher/list_questions/${quiz.test_id}`,
        {
          headers: getAuthHeaders(),
        }
      );
      const data = await response.json();
      if (response.ok) {
        setQuestions(data);
      }
    } catch (error) {
      console.error("Error fetching questions:", error);
    }
  };

  const handlePublish = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/teacher/publish_quiz/${quiz.test_id}`,
        {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify(publishForm),
        }
      );
      const data = await response.json();

      if (response.ok) {
        setMessage({ type: "success", text: "Quiz published successfully!" });
        setShowPublishModal(false);
        onUpdate();
      } else {
        setMessage({
          type: "error",
          text: data.error || "Failed to publish quiz",
        });
      }
    } catch (error) {
      setMessage({ type: "error", text: "Error publishing quiz" });
    }
    setLoading(false);
  };

  const handleModifyTime = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/teacher/modify_quiz/${quiz.test_id}`,
        {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({ extra_time: extraTime }),
        }
      );
      const data = await response.json();

      if (response.ok) {
        setMessage({
          type: "success",
          text: "Quiz duration updated successfully!",
        });
        setShowModifyModal(false);
        onUpdate();
      } else {
        setMessage({
          type: "error",
          text: data.error || "Failed to modify quiz",
        });
      }
    } catch (error) {
      setMessage({ type: "error", text: "Error modifying quiz" });
    }
    setLoading(false);
  };

  const getStatusBadge = (status) => {
    const colors = {
      not_published: "bg-gray-100 text-gray-800",
      published: "bg-blue-100 text-blue-800",
      active: "bg-green-100 text-green-800",
      completed: "bg-red-100 text-red-800",
    };
    return (
      <span
        className={`px-3 py-1 rounded-full text-sm font-medium ${colors[status]}`}
      >
        {status.replace("_", " ").toUpperCase()}
      </span>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <button
        onClick={onBack}
        className="mb-4 text-blue-600 hover:text-blue-800 flex items-center gap-2"
      >
        ← Back
      </button>

      {message.text && (
        <div
          className={`mb-4 p-4 rounded-lg flex items-center gap-2 ${
            message.type === "success"
              ? "bg-green-50 text-green-800"
              : "bg-red-50 text-red-800"
          }`}
        >
          {message.type === "success" ? (
            <CheckCircle size={20} />
          ) : (
            <AlertCircle size={20} />
          )}
          {message.text}
        </div>
      )}

      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold mb-2">{quizData.title}</h2>
            <p className="text-gray-600 mb-2">{quizData.description}</p>
            <div className="flex gap-2 items-center">
              {getStatusBadge(quizData.status)}
            </div>
          </div>
          <div className="flex gap-2">
            {quizData.status === "not_published" && (
              <button
                onClick={() => setShowPublishModal(true)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <Calendar size={18} />
                Publish Quiz
              </button>
            )}
            {quizData.status === "active" && (
              <button
                onClick={() => setShowModifyModal(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <Clock size={18} />
                Extend Time
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-gray-600 text-sm">Total Questions</div>
            <div className="text-2xl font-bold">{quizData.total_questions}</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-gray-600 text-sm">Total Marks</div>
            <div className="text-2xl font-bold">{quizData.total_marks}</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-gray-600 text-sm">Duration</div>
            <div className="text-2xl font-bold">
              {quizData.duration_minutes}m
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-gray-600 text-sm">Passing Marks</div>
            <div className="text-2xl font-bold">{quizData.passing_marks}</div>
          </div>
        </div>

        {quizData.start_time && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <div className="text-sm text-gray-600">Start Time</div>
            <div className="font-semibold">
              {new Date(quizData.start_time).toLocaleString()}
            </div>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4">
          Questions ({questions.length})
        </h3>
        <div className="space-y-4">
          {questions.map((q, idx) => (
            <div
              key={q.question_id}
              className="border rounded-lg p-4 hover:bg-gray-50"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-semibold">Q{idx + 1}.</span>
                    <span className="text-sm px-2 py-1 bg-gray-100 rounded">
                      {q.question_type.toUpperCase()}
                    </span>
                    <span className="text-sm px-2 py-1 bg-blue-100 rounded">
                      {q.difficulty_level}
                    </span>
                    <span className="text-sm px-2 py-1 bg-green-100 rounded">
                      {q.marks} marks
                    </span>
                  </div>
                  <p className="text-gray-800 mb-3">{q.question_text}</p>

                  {q.question_type!=="nat" && q.options && q.options.length > 0 && (
                    <div className="space-y-1 ml-4">
                      {q.options.map((opt) => (
                        <div key={opt.id} className="flex items-center gap-2">
                          <span className="font-medium">{opt.id}.</span>
                          <span>{opt.text}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="mt-2 text-sm text-gray-600">
                    <span className="font-medium">Correct Answer:</span>{" "}
                    {Array.isArray(q.correct_answer)
                      ? q.correct_answer.join(", ")
                      : q.correct_answer}
                  </div>

                  {q.tags && q.tags.length > 0 && (
                    <div className="mt-2 flex gap-1 flex-wrap">
                      {q.tags.map((tag, i) => (
                        <span
                          key={i}
                          className="text-xs px-2 py-1 bg-purple-100 text-purple-800 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Publish Modal */}
      {showPublishModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">Publish Quiz</h3>
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
                    start_time: e.target.value + ":00Z",
                  })
                }
                className="w-full p-2 border rounded-lg"
              />
              <p className="text-xs text-gray-500 mt-1">
                Select when students can start attempting the quiz
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handlePublish}
                disabled={loading || !publishForm.start_time}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? "Publishing..." : "Publish"}
              </button>
              <button
                onClick={() => setShowPublishModal(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modify Time Modal */}
      {showModifyModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">Extend Quiz Duration</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                Additional Time (minutes)
              </label>
              <input
                type="number"
                min="1"
                value={extraTime}
                onChange={(e) => setExtraTime(e.target.value)}
                className="w-full p-2 border rounded-lg"
              />
              <p className="text-xs text-gray-500 mt-1">
                Current duration: {quizData.duration_minutes} minutes
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleModifyTime}
                disabled={loading || !extraTime}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? "Updating..." : "Extend Time"}
              </button>
              <button
                onClick={() => setShowModifyModal(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeacherQuizManagement;