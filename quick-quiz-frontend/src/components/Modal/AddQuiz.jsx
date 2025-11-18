import React, { useState } from "react";
import Modal from "../Utils/Modal";
import InputField from "../Utils/InputField";
import SelectField from "../Utils/SelectField";
import Button from "../Utils/Button";

const AddQuiz = ({ show, onClose, courseId, onSubmit }) => {
  const [quizData, setQuizData] = useState({
    title: "",
    description: "",
    difficulty_level: "Medium",
    duration_minutes: 60,
    total_marks: 100,
    total_questions: 10,
    passing_marks: 40,
  });

  const handleSubmit = () => {
    onSubmit({
      ...quizData,
      course_id: courseId,
    });

    setQuizData({
      title: "",
      description: "",
      difficulty_level: "Medium",
      duration_minutes: 60,
      total_marks: 100,
      total_questions: 10,
      passing_marks: 40,
    });
  };

  return (
    <Modal show={show} onClose={onClose} title={`Add Quiz to ${courseId}`}>
      <div className="space-y-4">
        <InputField
          label="Quiz Title"
          value={quizData.title}
          onChange={(e) => setQuizData({ ...quizData, title: e.target.value })}
          required
        />
        <InputField
          label="Description"
          value={quizData.description}
          onChange={(e) =>
            setQuizData({ ...quizData, description: e.target.value })
          }
          rows="2"
        />
        <SelectField
          label="Difficulty Level"
          value={quizData.difficulty_level}
          onChange={(e) =>
            setQuizData({ ...quizData, difficulty_level: e.target.value })
          }
          options={["Easy", "Medium", "Hard"]}
        />
        <InputField
          label="Duration (minutes)"
          type="number"
          value={quizData.duration_minutes}
          onChange={(e) =>
            setQuizData({
              ...quizData,
              duration_minutes: parseInt(e.target.value),
            })
          }
          required
        />
        <InputField
          label="Total Questions"
          type="number"
          value={quizData.total_questions}
          onChange={(e) =>
            setQuizData({
              ...quizData,
              total_questions: parseInt(e.target.value),
            })
          }
          required
        />
        <div className="grid grid-cols-2 gap-4">
          <InputField
            label="Total Marks"
            type="number"
            value={quizData.total_marks}
            onChange={(e) =>
              setQuizData({
                ...quizData,
                total_marks: parseInt(e.target.value),
              })
            }
            required
          />
          <InputField
            label="Passing Marks"
            type="number"
            value={quizData.passing_marks}
            onChange={(e) =>
              setQuizData({
                ...quizData,
                passing_marks: parseInt(e.target.value),
              })
            }
            required
          />
        </div>
        <div className="flex gap-2 pt-2">
          <Button onClick={handleSubmit} variant="primary" className="flex-1">
            Create Quiz
          </Button>
          <Button onClick={onClose} variant="secondary" className="flex-1">
            Cancel
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default AddQuiz;
