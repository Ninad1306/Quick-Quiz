import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Users, Award, TrendingDown, ArrowLeft, BarChart3 } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../../constants';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const StatCard = ({ title, value, subtitle, icon: Icon, color }) => (
  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
    <div className="flex items-center justify-between mb-4">
      <div className={`p-3 rounded-full ${color} bg-opacity-10`}>
        <Icon className={color.replace('bg-', 'text-')} size={24} />
      </div>
      <span className="text-2xl font-bold text-gray-800">{value}</span>
    </div>
    <div>
      <h3 className="text-gray-500 text-sm font-medium uppercase tracking-wide">{title}</h3>
      {subtitle && <p className="text-gray-400 text-xs mt-1">{subtitle}</p>}
    </div>
  </div>
);

const TeacherAnalyticsDashboard = ({ quizId, onBack }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `${API_BASE_URL}/teacher/quiz_analytics/${quizId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setData(res.data);
      } catch (err) {
        console.error("Analytics fetch error:", err);
        setError(err.response?.data?.error || "Failed to load analytics");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [quizId]);

  if (loading) return <div className="p-12 text-center text-gray-500">Loading analytics...</div>;
  
  if (error) return (
    <div className="p-12 text-center">
      <p className="text-red-500 mb-4">{error}</p>
      <button onClick={onBack} className="text-blue-600 hover:underline">Go Back</button>
    </div>
  );

  if (!data) return null;

  const { metrics, topic_ranking } = data;

  // Prepare Chart Data
  const chartData = {
    labels: topic_ranking.map(t => t.topic),
    datasets: [
      {
        label: 'Total Marks Lost',
        data: topic_ranking.map(t => t.marks_lost),
        backgroundColor: 'rgba(239, 68, 68, 0.6)', // Red for "loss"
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Where Students Are Losing Marks (By Topic)' },
    },
    scales: {
      y: { beginAtZero: true, title: { display: true, text: 'Marks Lost' } }
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex items-center gap-3 mb-8">
        <BarChart3 className="text-blue-600" size={32} />
        <h1 className="text-3xl font-bold text-gray-800">Quiz Analytics</h1>
      </div>

      {/* 1. Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard 
          title="Class Average" 
          value={metrics.mean} 
          subtitle={`Median: ${metrics.median}`} 
          icon={Award} 
          color="bg-blue-500" 
        />
        <StatCard 
          title="Highest Score" 
          value={metrics.max} 
          subtitle={`Lowest: ${metrics.min}`} 
          icon={TrendingUp} 
          color="bg-green-500" 
        />
        <StatCard 
          title="Standard Dev." 
          value={metrics.std_dev} 
          subtitle="Score Spread" 
          icon={BarChart3} 
          color="bg-purple-500" 
        />
        <StatCard 
          title="Total Attempts" 
          value={metrics.count} 
          subtitle="Students submitted" 
          icon={Users} 
          color="bg-orange-500" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 2. Topic Loss Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <Bar data={chartData} options={chartOptions} />
        </div>

        {/* 3. Weak Topics List */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-fit">
          <div className="flex items-center gap-2 mb-6">
            <TrendingDown className="text-red-500" size={20} />
            <h3 className="text-lg font-bold text-gray-800">Top Weak Areas</h3>
          </div>
          
          <div className="space-y-4">
            {topic_ranking.slice(0, 5).map((topic, index) => (
              <div key={index} className="flex justify-between items-center border-b border-gray-100 pb-3 last:border-0">
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 flex items-center justify-center bg-gray-100 text-gray-600 rounded-full text-xs font-bold">
                    {index + 1}
                  </span>
                  <span className="font-medium text-gray-700">{topic.topic}</span>
                </div>
                <span className="text-red-600 font-semibold text-sm">
                  -{topic.marks_lost} marks
                </span>
              </div>
            ))}
            {topic_ranking.length === 0 && (
              <p className="text-gray-500 text-center italic">No data available yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Small helper component for icons if you don't have TrendingUp imported
const TrendingUp = ({ size, className }) => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round" 
    className={className}
  >
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
    <polyline points="17 6 23 6 23 12"></polyline>
  </svg>
);

export default TeacherAnalyticsDashboard;