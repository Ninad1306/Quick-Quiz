import React, { useEffect, useState } from "react";
import { DifficultyBarChart, TypePieChart } from "./Charts";
import axios from "axios";
import { API_BASE_URL } from "../../constants";

const StudentAnalytics = ({ attemptId, onBack }) => {
  const [data, setData] = useState(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `${API_BASE_URL}/student/quiz_analytics/${attemptId}`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (res.data.status === "pending") {
          setMsg(res.data.message);
        } else {
          setData(res.data.stats);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchData();
  }, [attemptId]);

  if (msg) return <div className="p-8 text-center text-gray-600">{msg}</div>;
  if (!data) return <div>Loading analytics...</div>;

  return (
    <div className="max-w-6xl mx-auto mb-8 p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-6">Performance Analysis</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-gray-50 p-4 rounded-lg">
          <DifficultyBarChart data={data.difficulty} />
        </div>
        <div className="bg-gray-50 p-4 rounded-lg w-2/3 mx-auto">
          <TypePieChart data={data.type} />
        </div>
      </div>

      <div className="mt-8">
        <h3 className="text-xl font-bold mb-4">Topic Breakdown</h3>
        <div className="grid grid-cols-1 gap-4">
          {Object.entries(data.tags).map(([tag, [obt, total]]) => (
            <div key={tag} className="flex items-center">
              <span className="w-32 font-medium">{tag}</span>
              <div className="flex-1 h-4 bg-gray-200 rounded-full mx-4">
                <div
                  className="h-full bg-green-500 rounded-full"
                  style={{ width: `${(obt / total) * 100}%` }}
                ></div>
              </div>
              <span className="text-sm text-gray-600">
                {obt}/{total}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StudentAnalytics;
