import React, { useState, useEffect } from "react";
import { API_BASE_URL } from "../../constants";
import axios from "axios";
import { BookOpen } from "lucide-react";
import Navbar from "../Utils/Navbar";
import Course from "../Course/Course";
import CourseCard from "../Course/CourseCard";
import AddCourse from "../Modal/AddCourse";
import EnrollCourse from "../Modal/EnrollCourse";
import AddQuiz from "../Modal/AddQuiz";
import TeacherQuizManagement from "../Quiz/TeacherQuizManagement";
import StudentQuizAttempt from "../Quiz/StudentQuizAttempt";

const MainPage = ({ user, onLogout }) => {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [currentView, setCurrentView] = useState("home");
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [showAddCourseModal, setShowAddCourseModal] = useState(false);
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const [showAddQuizModal, setShowAddQuizModal] = useState(false);
  const [availableCourses, setAvailableCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [quizzes, setQuizzes] = useState([]);

  useEffect(() => {
    fetchCourses(user.role);
  }, []);

  useEffect(() => {
    fetchQuizzes(user.role);
  }, [showAddQuizModal, selectedCourse]);

  const fetchQuizzes = async (role) => {
    setTimeout(async () => {
      let res;
      const headers = {
        Authorization: "Bearer " + localStorage.getItem("token"),
      };

      if (!selectedCourse) return;

      if (role === "teacher") {
        res = await axios.get(
          `${API_BASE_URL}/teacher/list_quiz/${selectedCourse?.course_id}`,
          {
            headers,
          }
        );
      } else {
        res = await axios.get(
          `${API_BASE_URL}/student/list_quizzes/${selectedCourse?.course_id}`,
          {
            headers,
          }
        );
      }

      setQuizzes(res.data);
    }, 500);
  };

  const fetchCourses = async (role) => {
    setLoading(true);
    setTimeout(async () => {
      const headers = {
        Authorization: "Bearer " + localStorage.getItem("token"),
      };

      if (role === "teacher") {
        const res = await axios.get(`${API_BASE_URL}/teacher/list_courses`, {
          headers,
        });
        setCourses(res.data);
      } else {
        const res = await axios.get(`${API_BASE_URL}/student/courses`, {
          headers,
        });
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

      const res = await axios.get(`${API_BASE_URL}/student/available`, {
        headers,
      });
      setAvailableCourses(res.data);
    }, 300);
  };

  const handleAddCourse = async (formData, setError, setLoading) => {
    setLoading(true);
    try {
      console.log("here");
      
      await axios.post(`${API_BASE_URL}/teacher/register_course`, formData, {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token"),
        },
      });
      setShowAddCourseModal(false);
      fetchCourses(user.role);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const onDeleteCourse = async (courseId) => {
    if (!confirm(`Are you sure you want to Delete ${courseId}?`)) {
      return;
    }

    const headers = {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    };
    const res = await axios.post(
      `${API_BASE_URL}/teacher/delete_course/${courseId}`,
      {},
      {
        headers,
      }
    );

    if (res.status === 200) {
      fetchCourses(user.role);
    }
  };

  const onUnenrollCourse = async (courseId) => {
    if (!confirm(`Are you sure you want to Unenroll from ${courseId}?`)) {
      return;
    }

    const headers = {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    };
    const res = await axios.delete(
      `${API_BASE_URL}/student/unenroll/${courseId}`,
      {
        headers,
      }
    );

    if (res.status === 200) {
      fetchCourses(user.role);
    }
  };

  const onDeleteQuiz = async (id) => {
    if (!confirm(`Are you sure you want to Delete Quiz ${id}?`)) {
      return;
    }

    const header = {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    };

    const res = await axios.post(
      `${API_BASE_URL}/teacher/delete_quiz/${id}`,
      {},
      { headers: header }
    );

    if (res.status === 200) {
      fetchQuizzes(user.role);
    }
  };

  const handleEnroll = async (courseId, setError) => {
    try {
      await axios.post(
        `${API_BASE_URL}/student/enroll`,
        { course_id: courseId },
        {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        }
      );

      setShowEnrollModal(false);
      fetchCourses(user.role);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    }
  };

  const handleCourseClick = (course) => {
    setSelectedCourse(course);
    setCurrentView("course");
  };

  const handleBackToCourses = () => {
    setSelectedCourse(null);
    setQuizzes([]);
    setCurrentView("home");
  };

  const handleQuizClick = (quiz, role) => {
    if (role === "student" && quiz.state === "published" && !quiz.can_attempt)
      return;
    setSelectedQuiz(quiz);
    setCurrentView("quiz");
  };

  const handleAddQuiz = async (quizData, setLoading, setError) => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/teacher/create_quiz`, quizData, {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token"),
        },
      });

      setShowAddQuizModal(false);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
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

  const content = () => {
    if (selectedQuiz) {
      if (user.role === "student") {
        return (
          <StudentQuizAttempt
            quiz={selectedQuiz}
            onBack={() => {
              setSelectedQuiz(null);
              setCurrentView("course");
            }}
          />
        );
      }

      return (
        <TeacherQuizManagement
          quiz={selectedQuiz}
          onBack={() => {
            setSelectedQuiz(null);
            setCurrentView("course");
          }}
        />
      );
    } else if (selectedCourse) {
      return (
        <Course
          course={selectedCourse}
          quizzes={quizzes}
          userRole={user.role}
          onBack={handleBackToCourses}
          onViewAnalytics={handleViewAnalytics}
          onClickQuiz={handleQuizClick}
          onDeleteQuiz={onDeleteQuiz}
        />
      );
    } else {
      return (
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
                  onDeleteCourse={onDeleteCourse}
                  onUnenrollCourse={onUnenrollCourse}
                />
              ))}
            </div>
          )}
        </main>
      );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar
        user={user}
        onLogout={onLogout}
        onAddCourse={() => setShowAddCourseModal(true)}
        onEnrollCourse={() => setShowEnrollModal(true)}
        onAddQuiz={() => setShowAddQuizModal(true)}
        onViewAnalytics={handleViewAnalytics}
        currentView={currentView}
      />

      {content()}

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
