import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement
);

export const DifficultyBarChart = ({ data }) => {    
  const chartData = {
    labels: ['easy', 'medium', 'hard'],
    datasets: [
      {
        label: 'Obtained',
        data: [data.easy[0], data.medium[0], data.hard[0]],
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
      {
        label: 'Total Possible',
        data: [data.easy[1], data.medium[1], data.hard[1]],
        backgroundColor: 'rgba(53, 162, 235, 0.3)',
      },
    ],
  };
  return <Bar data={chartData} options={{ responsive: true, plugins: { title: { display: true, text: 'Performance by Difficulty' } } }} />;
};

export const TypePieChart = ({ data }) => {
    // Calculate Percentage for each type
    const getPerc = (arr) => arr[1] > 0 ? (arr[0]/arr[1])*100 : 0;
    
    const chartData = {
        labels: ['MCQ', 'MSQ', 'NAT'],
        datasets: [{
            label: 'Accuracy (%)',
            data: [getPerc(data.mcq), getPerc(data.msq), getPerc(data.nat)],
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
        }]
    };
    return <Pie data={chartData} options={{ plugins: { title: { display: true, text: 'Accuracy by Type' } } }} />;
};

export const TrendLineChart = ({ labels, data }) => {
    const chartData = {
        labels,
        datasets: [{
            label: 'Quiz Score (%)',
            data,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    };
    return <Line data={chartData} options={{ plugins: { title: { display: true, text: 'Performance Trend' } } }} />;
};