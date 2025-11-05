import React from 'react';

const Button = ({ onClick, children, variant = 'primary', className = '', icon: Icon }) => {
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-700 hover:bg-gray-300',
    success: 'bg-green-600 text-white hover:bg-green-700',
    ghost: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
  };

  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-md transition flex items-center gap-2 ${variants[variant]} ${className}`}
    >
      {Icon && <Icon size={18} />}
      {children}
    </button>
  );
};

export default Button;