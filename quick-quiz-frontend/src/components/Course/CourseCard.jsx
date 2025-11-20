import React from "react";
import { BookOpen, GraduationCap } from "lucide-react";
import Button from "../Utils/Button";
import { API_BASE_URL } from "../../constants";
import axios from "axios";

const CourseCard = ({ course, userRole, onClick }) => {
  const onDeleteCourse = async (courseId) => {
    const headers = {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    };
    await axios.post(`${API_BASE_URL}/teacher/delete_course/${courseId}`, {}, {
      headers,
    });
    window.location.reload();
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition ">
      <div onClick={onClick} className="cursor-pointer">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-xl font-bold text-gray-800">
              {course.course_id}
            </h3>
            <p className="text-gray-600 mt-1">{course.course_name}</p>
          </div>
          <BookOpen className="text-blue-600" size={24} />
        </div>
        <div className="space-y-2 text-sm text-gray-600 mb-4">
          {userRole === "teacher" && (
            <>
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
                <GraduationCap size={16} />
                <span>{course.students_enrolled || 0} students enrolled</span>
              </div>
              <div className="text-sm text-gray-500">
                <span className="font-medium">Offered:</span>{" "}
                {course.offered_at?.join(", ")}
              </div>
            </>
          )}

          {userRole === "student" && (
            <div className="text-sm text-gray-500">
              <span className="font-medium">Enrolled:</span>{" "}
              {new Date(course.taken_at).toLocaleDateString()}
            </div>
          )}
        </div>
      </div>

      {userRole === "teacher" && (
        <Button
          onClick={() => onDeleteCourse(course.course_id)}
          variant="danger"
          className="w-full"
        >
          Delete
        </Button>
      )}
    </div>
  );
};

export default CourseCard;
