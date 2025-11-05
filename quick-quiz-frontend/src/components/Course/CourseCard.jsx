import React from 'react';
import { BookOpen, GraduationCap  } from 'lucide-react';

const CourseCard = ({ course, userRole, onClick }) => {
  return (
    <div 
      onClick={onClick}
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition cursor-pointer"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-800">{course.course_id}</h3>
          <p className="text-gray-600 mt-1">{course.course_name}</p>
        </div>
        <BookOpen className="text-blue-600" size={24} />
      </div>
      
      {userRole === 'teacher' && (
        <>
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
            <GraduationCap size={16} />
            <span>{course.students_enrolled || 0} students enrolled</span>
          </div>
          <div className="text-sm text-gray-500">
            <span className="font-medium">Offered:</span> {course.offered_at?.join(', ')}
          </div>
        </>
      )}
      
      {userRole === 'student' && (
        <div className="text-sm text-gray-500">
          <span className="font-medium">Enrolled:</span> {new Date(course.taken_at).toLocaleDateString()}
        </div>
      )}
    </div>
  );
};

export default CourseCard;