import React, { useState, useEffect } from "react";
import { Clock, AlertCircle, CheckCircle } from "lucide-react";
import { API_BASE_URL } from "../../constants";

const StudentQuizAttempt = ({ quiz, courseId, onBack }) => {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  useEffect(() => {
    fetchQuestions();
    calculateTimeRemaining();
  }, []);

  useEffect(() => {
    if (timeRemaining !== null && timeRemaining > 0 && !submitted) {
      const timer = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            handleAutoSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [timeRemaining, submitted]);

  const calculateTimeRemaining = () => {
    const startTime = new Date(quiz.start_time);
    const endTime = new Date(
      startTime.getTime() + quiz.duration_minutes * 60000
    );
    const now = new Date();
    const remaining = Math.floor((endTime - now) / 1000);
    setTimeRemaining(Math.max(0, remaining));
  };

  const fetchQuestions = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/student/quiz_questions/${quiz.test_id}`,
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

  const handleAnswerChange = (questionId, answer) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  };

  const handleAutoSubmit = async () => {
    if (!submitted) {
      await handleSubmit(true);
    }
  };

  const handleSubmit = async (isAuto = false) => {
    setIsSubmitting(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/student/submit_quiz/${quiz.test_id}`,
        {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({ answers }),
        }
      );
      const data = await response.json();

      if (response.ok) {
        setSubmitted(true);
        setMessage({
          type: "success",
          text: isAuto
            ? "Quiz auto-submitted (time expired)"
            : "Quiz submitted successfully!",
        });
      } else {
        setMessage({
          type: "error",
          text: data.error || "Failed to submit quiz",
        });
      }
    } catch (error) {
      setMessage({ type: "error", text: "Error submitting quiz" });
    }
    setIsSubmitting(false);
  };

  const formatTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs.toString().padStart(2, "0")}:${mins
      .toString()
      .padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  if (submitted) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          <CheckCircle size={64} className="mx-auto text-green-600 mb-4" />
          <h2 className="text-2xl font-bold mb-2">
            Quiz Submitted Successfully!
          </h2>
          <p className="text-gray-600 mb-6">
            Your answers have been recorded. Results will be available once the
            quiz is completed.
          </p>
          <button
            onClick={onBack}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            ← Back
          </button>
        </div>
      </div>
    );
  }

  const currentQ = questions[currentQuestion];

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">{quiz.title}</h2>
          <div
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              timeRemaining < 300
                ? "bg-red-100 text-red-800"
                : "bg-blue-100 text-blue-800"
            }`}
          >
            <Clock size={20} />
            <span className="font-mono font-bold">
              {formatTime(timeRemaining)}
            </span>
          </div>
        </div>

        <div className="flex gap-2 mb-4">
          <span className="text-sm px-3 py-1 bg-gray-100 rounded">
            Question {currentQuestion + 1} of {questions.length}
          </span>
          <span className="text-sm px-3 py-1 bg-gray-100 rounded">
            Answered: {Object.keys(answers).length} / {questions.length}
          </span>
        </div>

        <div className="h-2 bg-gray-200 rounded-full mb-6">
          <div
            className="h-full bg-blue-600 rounded-full transition-all"
            style={{
              width: `${((currentQuestion + 1) / questions.length) * 100}%`,
            }}
          />
        </div>
      </div>

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

      {currentQ && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-4">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm px-2 py-1 bg-blue-100 rounded">
              {currentQ.difficulty_level}
            </span>
            <span className="text-sm px-2 py-1 bg-green-100 rounded">
              {currentQ.marks} marks
            </span>
          </div>

          <h3 className="text-lg font-semibold mb-4">
            {currentQ.question_text}
          </h3>

          <div className="space-y-3">
            {currentQ.question_type === "mcq" &&
              currentQ.options?.map((opt) => (
                <label
                  key={opt.id}
                  className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="radio"
                    name={`question-${currentQ.question_id}`}
                    value={opt.id}
                    checked={answers[currentQ.question_id] === opt.id}
                    onChange={(e) =>
                      handleAnswerChange(currentQ.question_id, e.target.value)
                    }
                    className="w-4 h-4"
                  />
                  <span>
                    <strong>{opt.id}.</strong> {opt.text}
                  </span>
                </label>
              ))}

            {currentQ.question_type === "msq" &&
              currentQ.options?.map((opt) => (
                <label
                  key={opt.id}
                  className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    value={opt.id}
                    checked={(answers[currentQ.question_id] || []).includes(
                      opt.id
                    )}
                    onChange={(e) => {
                      const current = answers[currentQ.question_id] || [];
                      const newAnswer = e.target.checked
                        ? [...current, opt.id]
                        : current.filter((a) => a !== opt.id);
                      handleAnswerChange(currentQ.question_id, newAnswer);
                    }}
                    className="w-4 h-4"
                  />
                  <span>
                    <strong>{opt.id}.</strong> {opt.text}
                  </span>
                </label>
              ))}

            {currentQ.question_type === "nat" && (
              <input
                type="number"
                value={answers[currentQ.question_id] || ""}
                onChange={(e) =>
                  handleAnswerChange(
                    currentQ.question_id,
                    parseInt(e.target.value)
                  )
                }
                placeholder="Enter your answer"
                className="w-full p-3 border rounded-lg"
              />
            )}
          </div>
        </div>
      )}

      <div className="flex justify-between">
        <button
          onClick={() => setCurrentQuestion((prev) => Math.max(0, prev - 1))}
          disabled={currentQuestion === 0}
          className="px-6 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50"
        >
          Previous
        </button>

        {currentQuestion < questions.length - 1 ? (
          <button
            onClick={() => setCurrentQuestion((prev) => prev + 1)}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Next
          </button>
        ) : (
          <button
            onClick={() => handleSubmit(false)}
            disabled={isSubmitting}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {isSubmitting ? "Submitting..." : "Submit Quiz"}
          </button>
        )}
      </div>
    </div>
  );
};
