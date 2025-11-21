import React, { useEffect, useState } from 'react';
import { TrendLineChart } from './Charts'; // Import from your Charts file
import { Clock, AlertTriangle, TrendingUp } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../../constants';

const CourseAnalyticsDashboard = ({ courseId, onBack }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `${API_BASE_URL}/student/course_analytics/${courseId}`, 
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setData(res.data);
      } catch (err) {
        console.error("Failed to fetch course analytics", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [courseId]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    return `${mins} mins`;
  };

  if (loading) return <div className="p-8 text-center">Loading analytics...</div>;

  if (data?.message === "No data") {
    return (
      <div className="p-8 text-center">
        <h2 className="text-xl font-semibold text-gray-700">No Data Available</h2>
        <p className="text-gray-500 mb-4">Complete some quizzes to see your analytics.</p>
        <button onClick={onBack} className="text-blue-600 hover:underline">Back to Course</button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto p-6">
      <button 
        onClick={onBack} 
        className="mb-6 text-blue-600 hover:text-blue-800 flex items-center gap-2"
      >
        ← Back to Course
      </button>

      <h1 className="text-3xl font-bold text-gray-800 mb-8">Course Performance</h1>

      {/* --- Top Stats Row --- */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Avg Time Card */}
        <div className="bg-blue-50 p-6 rounded-xl border border-blue-100 flex items-center gap-4">
          <div className="p-3 bg-blue-100 rounded-full text-blue-600">
            <Clock size={24} />
          </div>
          <div>
            <p className="text-sm text-blue-600 font-semibold uppercase tracking-wide">Avg. Time / Quiz</p>
            <p className="text-2xl font-bold text-gray-800">{formatTime(data.avg_time_seconds)}</p>
          </div>
        </div>

        {/* Trend Summary Card */}
        <div className="bg-green-50 p-6 rounded-xl border border-green-100 flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-full text-green-600">
                <TrendingUp size={24} />
            </div>
            <div>
                <p className="text-sm text-green-600 font-semibold uppercase tracking-wide">Quizzes Taken</p>
                <p className="text-2xl font-bold text-gray-800">{data.trend.labels.length}</p>
            </div>
        </div>
      </div>

      {/* --- Charts Section --- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left: Trend Chart (Takes up 2 columns) */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Performance History</h3>
          <div className="h-64">
            <TrendLineChart labels={data.trend.labels} data={data.trend.data} />
          </div>
        </div>

        {/* Right: Weak Topics List */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="text-red-500" size={20} />
            <h3 className="text-lg font-bold text-gray-800">Areas for Improvement</h3>
          </div>
          
          {data.weak_topics.length > 0 ? (
            <div className="space-y-4">
              {data.weak_topics.map((topic, index) => (
                <div key={index}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-gray-700">{topic.topic}</span>
                    <span className="text-red-600 font-bold">{topic.accuracy}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-red-500 h-2 rounded-full" 
                      style={{ width: `${topic.accuracy}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm italic">
              Great job! No weak topics identified yet (Accuracy &gt; 60%).
            </p>
          )}
        </div>

      </div>
    </div>
  );
};

export default CourseAnalyticsDashboard;