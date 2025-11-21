import React, { useState, useEffect } from "react";
import { Clock, AlertCircle, CheckCircle, ArrowLeft } from "lucide-react";
import { API_BASE_URL } from "../../constants";
import axios from "axios";
import Button from "../Utils/Button";
import StudentAnalytics from "../Analytics/StudentAnalytics";

const StudentQuizAttempt = ({ quiz, onBack }) => {
  const [attemptId, setAttemptId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [scoreData, setScoreData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAnalytics, setShowAnalytics] = useState(false);
  let content;

  useEffect(() => {
    const initializeQuiz = async () => {
      try {
        const token = localStorage.getItem("token");
        const headers = { Authorization: `Bearer ${token}` };

        const startRes = await axios.post(
          `${API_BASE_URL}/student/start_attempt/${quiz.test_id}`,
          {},
          { headers }
        );
        const data = startRes.data;

        if (data.message === "Test already submitted") {
          setSubmitted(true);
          const currentTime = new Date().toISOString();
          setScoreData({
            total_score: data.total_score,
            per_question: [],
            attempt_id: data.attempt_id,
          });
          if (data.end_time && data.end_time >= currentTime) {
            setShowAnalytics(false);
          } else {
            setShowAnalytics(true);
            setAttemptId(data.attempt_id);
          }
          setLoading(false);
          return;
        }

        const newAttemptId = data.attempt_id;
        setAttemptId(newAttemptId);

        const qRes = await axios.get(
          `${API_BASE_URL}/student/list_questions/${quiz.test_id}`,
          { headers }
        );
        setQuestions(qRes.data.questions);

        calculateTimeRemaining();
        setLoading(false);
      } catch (err) {
        console.error("Initialization error:", err);
        setError(
          err.response?.data?.error ||
            "Failed to load quiz. It might not be active."
        );
        setLoading(false);
      }
    };

    initializeQuiz();
  }, [quiz.test_id]);

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

  const formatTime = (seconds) => {
    if (seconds === null) return "--:--";
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs > 0 ? hrs + ":" : ""}${mins
      .toString()
      .padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
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
    if (!attemptId) return;

    setIsSubmitting(true);
    try {
      const formattedAnswers = Object.keys(answers).map((qId) => ({
        question_id: parseInt(qId),
        selected_options: answers[qId],
      }));

      const token = localStorage.getItem("token");
      const response = await axios.post(
        `${API_BASE_URL}/student/submit_attempt/${attemptId}`,
        { answers: formattedAnswers },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setSubmitted(true);
      setScoreData(response.data);
    } catch (err) {
      console.error("Submit error:", err);
      alert("Failed to submit quiz. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-gray-500">Loading Quiz...</div>;
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <div className="text-red-600 mb-4 text-lg">{error}</div>
        <Button onClick={onBack} variant="secondary">
          Back to Course
        </Button>
      </div>
    );
  }

  if (submitted) {
    return (
      <div>
        <div className="max-w-3xl mx-auto p-6 mt-8">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <CheckCircle size={64} className="mx-auto text-green-600 mb-4" />
            <h2 className="text-3xl font-bold mb-2 text-gray-800">
              Quiz Submitted!
            </h2>

            {scoreData && (
              <div className="my-6 p-6 bg-blue-50 rounded-xl border border-blue-100">
                <p className="text-gray-600 mb-2 uppercase tracking-wide text-sm font-semibold">
                  Your Score
                </p>
                <p className="text-5xl font-bold text-blue-600">
                  {scoreData.total_score}{" "}
                  <span className="text-2xl text-gray-400">
                    / {quiz.total_marks}
                  </span>
                </p>
              </div>
            )}

            <p className="text-gray-600 mb-8">
              Your answers have been recorded successfully.
            </p>
            <Button onClick={onBack} variant="primary" className="mx-auto">
              Back to Course
            </Button>
          </div>
        </div>

        {showAnalytics && (
          <StudentAnalytics attemptId={attemptId} onBack={onBack} />
        )}
      </div>
    );
  }

  const currentQ = questions[currentQuestionIndex];

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6 border border-gray-100">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">{quiz.title}</h2>
            <p className="text-gray-500 text-sm">
              Question {currentQuestionIndex + 1} of {questions.length}
            </p>
          </div>

          <div
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-mono font-bold text-lg border ${
              timeRemaining < 300
                ? "bg-red-50 text-red-600 border-red-100"
                : "bg-blue-50 text-blue-600 border-blue-100"
            }`}
          >
            <Clock size={20} />
            <span>{formatTime(timeRemaining)}</span>
          </div>
        </div>

        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 transition-all duration-300 ease-out"
            style={{
              width: `${
                ((currentQuestionIndex + 1) / questions.length) * 100
              }%`,
            }}
          />
        </div>
      </div>

      {currentQ && (
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8 border border-gray-100 min-h-[400px] flex flex-col">
          <div className="flex items-start gap-3 mb-6">
            <span className="bg-gray-100 text-gray-600 font-bold px-3 py-1 rounded text-sm">
              {currentQ.difficulty_level?.toUpperCase()}
            </span>
            <span className="bg-gray-100 text-gray-600 font-bold px-3 py-1 rounded text-sm">
              {currentQ.marks} Marks
            </span>
            <span className="ml-auto bg-indigo-50 text-indigo-700 font-bold px-3 py-1 rounded text-sm uppercase">
              {currentQ.question_type}
            </span>
          </div>

          <h3 className="text-xl font-medium text-gray-800 mb-8 leading-relaxed">
            <span className="font-bold text-gray-400 mr-2">
              {currentQuestionIndex + 1}.
            </span>
            {currentQ.question_text}
          </h3>

          <div className="space-y-3 flex-grow">
            {currentQ.question_type === "mcq" &&
              currentQ.options?.map((opt) => (
                <label
                  key={opt.id}
                  className={`flex items-center gap-4 p-4 border rounded-xl cursor-pointer transition-all ${
                    answers[currentQ.question_id] === opt.id
                      ? "border-blue-500 bg-blue-50 text-blue-800"
                      : "border-gray-200 hover:border-blue-200 hover:bg-gray-50"
                  }`}
                >
                  <div
                    className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                      answers[currentQ.question_id] === opt.id
                        ? "border-blue-500"
                        : "border-gray-300"
                    }`}
                  >
                    {answers[currentQ.question_id] === opt.id && (
                      <div className="w-3 h-3 rounded-full bg-blue-500" />
                    )}
                  </div>
                  <input
                    type="radio"
                    name={`question-${currentQ.question_id}`}
                    value={opt.id}
                    checked={answers[currentQ.question_id] === opt.id}
                    onChange={(e) =>
                      handleAnswerChange(currentQ.question_id, e.target.value)
                    }
                    className="hidden"
                  />
                  <span className="font-medium">{opt.text}</span>
                </label>
              ))}

            {currentQ.question_type === "msq" &&
              currentQ.options?.map((opt) => {
                const isSelected = (
                  answers[currentQ.question_id] || []
                ).includes(opt.id);
                return (
                  <label
                    key={opt.id}
                    className={`flex items-center gap-4 p-4 border rounded-xl cursor-pointer transition-all ${
                      isSelected
                        ? "border-blue-500 bg-blue-50 text-blue-800"
                        : "border-gray-200 hover:border-blue-200 hover:bg-gray-50"
                    }`}
                  >
                    <div
                      className={`w-6 h-6 rounded border-2 flex items-center justify-center ${
                        isSelected
                          ? "border-blue-500 bg-blue-500"
                          : "border-gray-300"
                      }`}
                    >
                      {isSelected && (
                        <CheckCircle size={16} className="text-white" />
                      )}
                    </div>
                    <input
                      type="checkbox"
                      value={opt.id}
                      checked={isSelected}
                      onChange={(e) => {
                        const current = answers[currentQ.question_id] || [];
                        const newAnswer = e.target.checked
                          ? [...current, opt.id]
                          : current.filter((a) => a !== opt.id);
                        handleAnswerChange(currentQ.question_id, newAnswer);
                      }}
                      className="hidden"
                    />
                    <span className="font-medium">{opt.text}</span>
                  </label>
                );
              })}

            {currentQ.question_type === "nat" && (
              <div className="mt-4">
                <input
                  type="number"
                  value={answers[currentQ.question_id] || ""}
                  onChange={(e) =>
                    handleAnswerChange(
                      currentQ.question_id,
                      parseFloat(e.target.value)
                    )
                  }
                  placeholder="Enter your numerical answer"
                  className="w-full p-4 border-2 border-gray-200 rounded-xl text-lg focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all"
                />
              </div>
            )}
          </div>
        </div>
      )}

      <div className="flex justify-between items-center pt-4 border-t border-gray-200">
        <Button
          variant="secondary"
          onClick={() =>
            setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))
          }
          disabled={currentQuestionIndex === 0}
          icon={ArrowLeft}
        >
          Previous
        </Button>

        {currentQuestionIndex < questions.length - 1 ? (
          <Button
            variant="primary"
            onClick={() => setCurrentQuestionIndex((prev) => prev + 1)}
          >
            Next Question
          </Button>
        ) : (
          <Button
            variant="success"
            onClick={() => handleSubmit(false)}
            disabled={isSubmitting}
            className="px-8"
          >
            {isSubmitting ? "Submitting..." : "Submit Quiz"}
          </Button>
        )}
      </div>
    </div>
  );
};

export default StudentQuizAttempt;
