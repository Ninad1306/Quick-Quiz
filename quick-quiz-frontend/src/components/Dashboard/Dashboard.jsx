import React, { useState, useEffect } from "react";
import axios from "axios";
import { BookOpen } from "lucide-react";
import Navbar from "../Utils/Navbar";
import Course from "../Course/Course";
import CourseCard from "../Course/CourseCard";
import AddCourse from "../Modal/AddCourse";
import EnrollCourse from "../Modal/EnrollCourse";
import AddQuiz from "../Modal/AddQuiz";

const API_BASE_URL = 'http://localhost:5000';
const MainPage = ({ user, onLogout }) => {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [showAddCourseModal, setShowAddCourseModal] = useState(false);
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const [showAddQuizModal, setShowAddQuizModal] = useState(false);
  const [availableCourses, setAvailableCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCourses(user.role);
  }, []);

  const fetchCourses = async (role) => {
    setLoading(true);
    setTimeout(async () => {
      const headers = {
        Authorization: "Bearer " + localStorage.getItem("token"),
      };

      if (role === "teacher") {
        const res = await axios.get(`${API_BASE_URL}/teacher/list_courses`, { headers });
        setCourses(res.data);
      } else {
        const res = await axios.get(`${API_BASE_URL}/student/courses`, { headers });
        setCourses(res.data);
      }
      setLoading(false);
    }, 500);
  };

  const fetchAvailableCourses = async () => {
    setTimeout(async () => {
      const headers = {
        Authorization: "Bearer " + localStorage.getItem("token"),
      };
      
      const res = await axios.get(`${API_BASE_URL}/student/available`, { headers });
      setAvailableCourses(res.data);
    }, 300);
  };

  const handleAddCourse = (formData) => {
    console.log("Registering course:", formData);
    setShowAddCourseModal(false);
    fetchCourses(user.role);
  };

  const handleEnroll = (courseId) => {
    console.log("Enrolling in course:", courseId);
    setShowEnrollModal(false);
    fetchCourses(user.role);
  };

  const handleCourseClick = (course) => {
    setSelectedCourse(course);
  };

  const handleBackToCourses = () => {
    setSelectedCourse(null);
  };

  const handleAddQuiz = (quizData) => {
    console.log("Creating quiz:", quizData);
    setShowAddQuizModal(false);
  };

  const handleViewAnalytics = () => {
    console.log("View analytics for:", selectedCourse?.course_id);
  };

  useEffect(() => {
    if (showEnrollModal) {
      fetchAvailableCourses();
    }
  }, [showEnrollModal]);

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar
        user={user}
        onLogout={onLogout}
        onAddCourse={() => setShowAddCourseModal(true)}
        onEnrollCourse={() => setShowEnrollModal(true)}
        showCourseActions={!!selectedCourse}
        onAddQuiz={() => setShowAddQuizModal(true)}
        onViewAnalytics={handleViewAnalytics}
        onBack={handleBackToCourses}
      />

      {selectedCourse ? (
        <Course
          course={selectedCourse}
          userRole={user.role}
          onBack={handleBackToCourses}
          onAddQuiz={() => setShowAddQuizModal(true)}
          onViewAnalytics={handleViewAnalytics}
        />
      ) : (
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6">
            <h2 className="text-3xl font-bold text-gray-800">
              {user.role === "teacher" ? "My Courses" : "Enrolled Courses"}
            </h2>
            <p className="text-gray-600 mt-1">
              {user.role === "teacher"
                ? "Manage your courses and create quizzes"
                : "View your enrolled courses and take quizzes"}
            </p>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : courses.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <BookOpen className="mx-auto text-gray-400 mb-4" size={48} />
              <p className="text-xl text-gray-600">No courses found</p>
              <p className="text-gray-500 mt-2">
                {user.role === "teacher"
                  ? 'Click "Add Course" to register a new course'
                  : 'Click "Enroll Course" to join a course'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {courses.map((course) => (
                <CourseCard
                  key={course.course_id}
                  course={course}
                  userRole={user.role}
                  onClick={() => handleCourseClick(course)}
                />
              ))}
            </div>
          )}
        </main>
      )}

      <AddCourse
        show={showAddCourseModal}
        onClose={() => setShowAddCourseModal(false)}
        onSubmit={handleAddCourse}
      />

      <EnrollCourse
        show={showEnrollModal}
        onClose={() => setShowEnrollModal(false)}
        courses={availableCourses}
        onEnroll={handleEnroll}
      />

      <AddQuiz
        show={showAddQuizModal}
        onClose={() => setShowAddQuizModal(false)}
        courseId={selectedCourse?.course_id}
        onSubmit={handleAddQuiz}
      />
    </div>
  );
};

export default MainPage;
