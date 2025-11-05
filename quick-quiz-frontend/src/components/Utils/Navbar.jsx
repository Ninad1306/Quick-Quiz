import React from 'react';
import { BookOpen, Plus, User, LogOut, ArrowLeft, BarChart3 } from 'lucide-react';
import Button from './Button';

const Navbar = ({ user, onLogout, onAddCourse, onEnrollCourse, showCourseActions, onAddQuiz, onViewAnalytics, onBack }) => {
  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-3">
            {showCourseActions && (
              <button onClick={onBack} className="text-gray-600 hover:text-gray-800 mr-2">
                <ArrowLeft size={24} />
              </button>
            )}
            <BookOpen className="text-blue-600" size={32} />
            <h1 className="text-2xl font-bold text-gray-800">Learning Portal</h1>
          </div>
          
          <div className="flex items-center gap-4">
            {showCourseActions && user?.role === 'teacher' && (
              <>
                <Button onClick={onAddQuiz} variant="primary" icon={Plus}>
                  Add Quiz
                </Button>
                <Button onClick={onViewAnalytics} variant="ghost" icon={BarChart3}>
                  Analytics
                </Button>
              </>
            )}
            
            {!showCourseActions && user?.role === 'teacher' && (
              <Button onClick={onAddCourse} variant="primary" icon={Plus}>
                Add Course
              </Button>
            )}
            
            {!showCourseActions && user?.role === 'student' && (
              <Button onClick={onEnrollCourse} variant="success" icon={Plus}>
                Enroll Course
              </Button>
            )}
            
            <div className="flex items-center gap-2 text-gray-700">
              <User size={20} />
              <span className="font-medium">{user?.name}</span>
              <span className="text-sm text-gray-500">({user?.role})</span>
            </div>
            
            <button onClick={onLogout} className="text-gray-600 hover:text-gray-800 transition" title="Logout">
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;