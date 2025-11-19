import React, { useState, useEffect } from "react";
import { BookOpen, FileText } from "lucide-react";
import { API_BASE_URL } from "../../constants";
import axios from "axios";
import Button from "../Utils/Button";

const Course = ({ course, quizzes, userRole, onBack, onAddQuiz, onViewAnalytics }) => {
  

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-3xl font-bold text-gray-800">
              {course.course_id}
            </h2>
            <p className="text-xl text-gray-600 mt-2">{course.course_name}</p>
          </div>
          <BookOpen className="text-blue-600" size={48} />
        </div>

        {course.course_objectives && (
          <div className="mt-4">
            <h3 className="font-semibold text-gray-700 mb-2">
              Course Objectives
            </h3>
            <p className="text-gray-600">{course.course_objectives}</p>
          </div>
        )}

        <div className="mt-4 flex gap-4 text-sm text-gray-600">
          <div>
            <span className="font-medium">Level:</span> {course.course_level}
          </div>
          {userRole === "teacher" && (
            <>
              <div>
                <span className="font-medium">Students:</span>{" "}
                {course.students_enrolled || 0}
              </div>
              <div>
                <span className="font-medium">Offered:</span>{" "}
                {course.offered_at?.join(", ")}
              </div>
            </>
          )}
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-4">
          Quizzes & Tests
        </h3>
        {quizzes.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <FileText className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-xl text-gray-600">No quizzes available</p>
            {userRole === "teacher" && (
              <p className="text-gray-500 mt-2">
                Click "Add Quiz" in the navbar to create one
              </p>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quizzes.map((quiz) => (
              <div
                key={quiz.test_id}
                className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition"
              >
                <div className="flex justify-between items-start mb-3">
                  <h4 className="font-bold text-lg text-gray-800">
                    {quiz.title}
                  </h4>
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      quiz.difficulty_level === "Easy"
                        ? "bg-green-100 text-green-700"
                        : quiz.difficulty_level === "Medium"
                        ? "bg-yellow-100 text-yellow-700"
                        : "bg-red-100 text-red-700"
                    }`}
                  >
                    {quiz.difficulty_level}
                  </span>
                </div>

                <div className="space-y-2 text-sm text-gray-600 mb-4">
                  <div className="flex justify-between">
                    <span>Duration:</span>
                    <span className="font-medium">
                      {quiz.duration_minutes} min
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Marks:</span>
                    <span className="font-medium">{quiz.total_marks}</span>
                  </div>
                  {quiz.published_at && (
                    <div className="flex justify-between">
                      <span>Published:</span>
                      <span className="font-medium">
                        {new Date(quiz.published_at).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                <Button
                  onClick={() => console.log("View quiz:", quiz.test_id)}
                  variant="primary"
                  className="w-full"
                >
                  {userRole === "teacher" ? "Manage" : "Take Quiz"}
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Course;
