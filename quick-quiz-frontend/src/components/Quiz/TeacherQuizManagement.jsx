import React, { useState, useEffect } from "react";
import { Clock, AlertCircle, CheckCircle, Calendar } from "lucide-react";
import { API_BASE_URL } from "../../constants";
import DropdownButton from "../Utils/DropdownButton";
import AddQuestions from "../Modal/AddQuestions";
import DeleteQuestions from "../Modal/DeleteQuestions";
import ModifyDuration from "../Modal/ModifyDuration";
import AddManualQuestion from "../Modal/AddManualQuestion";
import PublishQuiz from "../Modal/PublishQuiz";
import axios from "axios";

const getAuthHeaders = () => ({
  Authorization: `Bearer ${localStorage.getItem("token")}`,
  "Content-Type": "application/json",
});

const TeacherQuizManagement = ({ quiz, onBack }) => {
  const [quizData, setQuizData] = useState(quiz);
  const [questions, setQuestions] = useState([]);
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });
  const [showAddQuestions, setShowAddQuestions] = useState(false);
  const [showDeleteQuestions, setShowDeleteQuestions] = useState(false);
  const [showModifyDuration, setShowModifyDuration] = useState(false);
  const [showAddManual, setShowAddManual] = useState(false);

  useEffect(() => {
    fetchQuestions();
  }, [quiz.test_id, showAddQuestions, showDeleteQuestions, showAddManual]);

  const fetchQuestions = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/teacher/list_questions/${quiz.test_id}`,
        {
          headers: getAuthHeaders(),
        }
      );

      const data = response.data;

      if (response.statusText === "OK") {
        setQuestions(data);
      }
    } catch (error) {
      console.error("Error fetching questions:", error);
    }
  };

  const handlePublish = async (publishForm) => {
    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/teacher/publish_quiz/${quiz.test_id}`,
        publishForm,
        {
          headers: getAuthHeaders(),
        }
      );

      const data = response.data;

      if (response.statusText === "OK") {
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

  // const handleModifyTime = async () => {
  //   setLoading(true);
  //   try {
  //     const response = await axios.post(
  //       `${API_BASE_URL}/teacher/modify_quiz/${quiz.test_id}`,
  //       { extra_time: extraTime },
  //       {
  //         headers: getAuthHeaders(),
  //       }
  //     );

  //     const data = response.data;

  //     if (response.statusText === "OK") {
  //       setMessage({
  //         type: "success",
  //         text: "Quiz duration updated successfully!",
  //       });
  //       setShowModifyModal(false);
  //       onUpdate();
  //     } else {
  //       setMessage({
  //         type: "error",
  //         text: data.error || "Failed to modify quiz",
  //       });
  //     }
  //   } catch (error) {
  //     setMessage({ type: "error", text: "Error modifying quiz" });
  //   }
  //   setLoading(false);
  // };

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

            {
              <DropdownButton
                onAddQuestions={() => setShowAddQuestions(true)}
                onAddManualQuestion={() => setShowAddManual(true)}
                onDeleteQuestions={() => setShowDeleteQuestions(true)}
                onModifyDuration={() => setShowModifyDuration(true)}
              />
            }
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

                  {q.question_type !== "nat" &&
                    q.options &&
                    q.options.length > 0 && (
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
        <PublishQuiz
          show={showPublishModal}
          onClose={() => setShowPublishModal(false)}
          onSubmit={handlePublish}
          loading={loading}
        />
      )}

      <AddQuestions
        show={showAddQuestions}
        onClose={() => setShowAddQuestions(false)}
        quizId={quiz?.test_id}
      />

      <DeleteQuestions
        show={showDeleteQuestions}
        onClose={() => setShowDeleteQuestions(false)}
        questions={questions}
        quizId={quiz?.test_id}
      />

      <ModifyDuration
        show={showModifyDuration}
        onClose={() => setShowModifyDuration(false)}
        quizId={quiz?.test_id}
        currentDuration={quiz?.duration_minutes}
      />

      <AddManualQuestion
        show={showAddManual}
        onClose={() => setShowAddManual(false)}
        quizId={quiz?.test_id}
      />
    </div>
  );
};

export default TeacherQuizManagement;
