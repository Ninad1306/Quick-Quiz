import React, { useState } from 'react';
import Modal from '../Utils/Modal';
import InputField from '../Utils/InputField';
import SelectField from '../Utils/SelectField';
import Button from '../Utils/Button';

const AddCourse = ({ show, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    course_id: '',
    course_name: '',
    course_level: 'Postgraduate',
    course_objectives: '',
    offered_at: 'Fall_2025'
  });

  const courseLevels = ['Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6', 'Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11', 'Grade 12', 'Undergraduate', 'Postgraduate'];

  const handleSubmit = () => {
    onSubmit(formData);
    setFormData({
      course_id: '',
      course_name: '',
      course_level: 'Postgraduate',
      course_objectives: '',
      offered_at: '2025'
    });
  };

  return (
    <Modal show={show} onClose={onClose} title="Register New Course">
      <div className="space-y-4">
        <InputField
          label="Course ID"
          value={formData.course_id}
          onChange={(e) => setFormData({...formData, course_id: e.target.value})}
          maxLength="8"
          required
        />
        <InputField
          label="Course Name"
          value={formData.course_name}
          onChange={(e) => setFormData({...formData, course_name: e.target.value})}
          required
        />
        <SelectField
          label="Course Level"
          value={formData.course_level}
          onChange={(e) => setFormData({...formData, course_level: e.target.value})}
          options={courseLevels}
        />
        <InputField
          label="Offered At"
          value={formData.offered_at}
          onChange={(e) => setFormData({...formData, offered_at: e.target.value})}
          placeholder="e.g., 2025"
          required
        />
        <InputField
          label="Course Objectives (Optional)"
          value={formData.course_objectives}
          onChange={(e) => setFormData({...formData, course_objectives: e.target.value})}
          rows="3"
        />
        <div className="flex gap-2 pt-2">
          <Button onClick={handleSubmit} variant="primary" className="flex-1">
            Register Course
          </Button>
          <Button onClick={onClose} variant="secondary" className="flex-1">
            Cancel
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default AddCourse;