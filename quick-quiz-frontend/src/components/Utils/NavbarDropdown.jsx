import React from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import Button from "./Button";

const NavbarDropdown = () => {
  return (
    <div className="relative group z-50">
      <Button>Modify Quiz</Button>

      <div className="absolute left-0 mt-0 w-48 bg-white text-gray-800 rounded-md shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 ease-in-out transform group-hover:translate-y-0 translate-y-2 border border-gray-100">
        <div className="relative group/nested border-b border-gray-100 last:border-0">
          <button className="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center justify-between">
            <span>Add Questions</span>
            <ChevronRight size={14} className="text-gray-400" />
          </button>

          <div className="absolute left-full top-0 w-40 bg-white text-gray-800 rounded-md shadow-xl opacity-0 invisible group-hover/nested:opacity-100 group-hover/nested:visible transition-all duration-200 ml-1 border border-gray-100">
            <button
              onClick={() => handleMenuAction("add-auto")}
              className="w-full text-left block px-4 py-2 hover:bg-blue-50 hover:text-blue-600 text-sm"
            >
              Automatic
            </button>

            <button
              onClick={() => handleMenuAction("add-manual")}
              className="w-full text-left block px-4 py-2 hover:bg-blue-50 hover:text-blue-600 text-sm"
            >
              Manual
            </button>
          </div>
        </div>

        <button
          onClick={() => handleMenuAction("delete")}
          className="w-full text-left block px-4 py-3 hover:bg-red-50 hover:text-red-600 border-b border-gray-100 last:border-0"
        >
          Delete Questions
        </button>

        <button
          onClick={() => handleMenuAction("time")}
          className="w-full text-left block px-4 py-3 hover:bg-gray-50 last:border-0"
        >
          Modify Time
        </button>
      </div>
    </div>
  );
};

export default NavbarDropdown;
