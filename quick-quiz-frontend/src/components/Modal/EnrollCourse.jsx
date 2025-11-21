import React from "react";
import Modal from "../Utils/Modal";
import Button from "../Utils/Button";

const EnrollCourse = ({ show, onClose, courses, onEnroll }) => {
  return (
    <Modal show={show} onClose={onClose} title="Enroll in Course">
      <div className="space-y-3">
        {courses.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No available courses</p>
        ) : (
          courses.map((course) => (
            <div
              key={course.course_id}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-400 transition"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-semibold text-lg">{course.course_id}</h3>
                  <p className="text-gray-600">{course.course_name}</p>
                </div>
              </div>
              <Button
                onClick={() => onEnroll(course.course_id)}
                variant="success"
                className="w-full mt-2"
              >
                Enroll
              </Button>
            </div>
          ))
        )}
      </div>
      <Button onClick={onClose} variant="secondary" className="w-full mt-4">
        Close
      </Button>
    </Modal>
  );
};

export default EnrollCourse;
