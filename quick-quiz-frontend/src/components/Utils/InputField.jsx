import React from "react";

const InputField = ({
  label,
  type = "text",
  value,
  onChange,
  required,
  placeholder,
  maxLength,
  rows,
}) => {
  const Component = rows ? "textarea" : "input";

  return (
    <div>
      <label className="block text-sm font-medium mb-1">{label}</label>
      <Component
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        placeholder={placeholder}
        maxLength={maxLength}
        rows={rows}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );
};

export default InputField;
