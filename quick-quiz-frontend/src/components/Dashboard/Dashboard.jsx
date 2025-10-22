import React from 'react';

function Dashboard({ user, onLogout }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
            <button
              onClick={onLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Welcome, {user.name}!
          </h2>
          <div className="space-y-2 text-gray-600">
            <p><span className="font-semibold">Email:</span> {user.email}</p>
            <p><span className="font-semibold">Role:</span> <span className="capitalize">{user.role}</span></p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;