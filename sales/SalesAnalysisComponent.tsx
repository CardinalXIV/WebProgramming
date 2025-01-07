import React, { useEffect, useState } from 'react';
import SalesNav from '@/components/sales/SalesNav';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import moment from 'moment';
import { SalesAPI } from '@/services/api'; // Adjust the import path as necessary

interface SalesData {
  total_revenue: number;
  total_sales: number;
  money_growth: number;
  sales_growth: number;
  sales_by_product: any[];
}

const SalesAnalysisComponent: React.FC = () => {
  const [data, setData] = useState<SalesData>({
    total_revenue: 0,
    total_sales: 0,
    money_growth: 0,
    sales_growth: 0,
    sales_by_product: [],
  });
  const [trendData, setTrendData] = useState<any>(null);
  const [trendType, setTrendType] = useState<string>('SMA');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [error, setError] = useState<string>('');

  const salesAPI = new SalesAPI(); // Create an instance of the SalesAPI class

  useEffect(() => {
    salesAPI.getSalesOverview('today')
      .then((response) => setData(response.data)) // Access the data directly
      .catch((error) => console.error('Error fetching sales data:', error));
  }, []);

  const fetchTrendData = async () => {
    if (!startDate || !endDate) {
      setError('Please select both start and end dates.');
      return;
    }
    setError(''); // Clear any previous error messages
    try {
      const response = await salesAPI.getSalesTrendData(startDate, endDate, trendType);
      console.log('Fetched Trend Data:', response.data);
      setTrendData(response.data); // Access the data directly
    } catch (error) {
      console.error('Error loading trend data:', error);
    }
  };

  const handleTrendChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setTrendType(event.target.value);
  };

  const handleStartDateChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setStartDate(event.target.value);
  };

  const handleEndDateChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setEndDate(event.target.value);
  };

  const handleDisplayClick = () => {
    fetchTrendData();
  };

  const chartData = trendData?.months.map((month: string, index: number) => ({
    month: moment(month).format('YYYY-MM'), // Format the month correctly
    total_revenue: trendData.total_revenue[index],
    sma_revenue: trendData.sma_revenue[index],
    ema_revenue: trendData.ema_revenue[index],
  }));

  const peakSalesMonth = chartData ? chartData.reduce((prev: any, current: any) => (prev.total_revenue > current.total_revenue ? prev : current), chartData[0]).month : 'N/A';
  const lowestSalesMonth = chartData ? chartData.reduce((prev: any, current: any) => (prev.total_revenue < current.total_revenue ? prev : current), chartData[0]).month : 'N/A';

  const trendDirection = chartData && chartData[chartData.length - 1].total_revenue > chartData[0].total_revenue ? 'UP' : 'DOWN';

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <SalesNav />
      <header className="bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-white">Sales Analysis</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-bold mb-4">Trend line option</h2>
            <select
              className="bg-gray-700 text-white p-2 rounded w-full mb-4"
              value={trendType}
              onChange={handleTrendChange}
            >
              <option value="SMA">Simple Moving Average</option>
              <option value="EMA">Exponential Moving Average</option>
            </select>
            <h2 className="text-xl font-bold mb-4">Table Parameters</h2>
            <div className="grid grid-cols-1 gap-4">
              <input
                type="date"
                className="bg-gray-700 text-white p-2 rounded"
                value={startDate}
                onChange={handleStartDateChange}
              />
              <input
                type="date"
                className="bg-gray-700 text-white p-2 rounded"
                value={endDate}
                onChange={handleEndDateChange}
              />
            </div>
            {error && <p className="text-red-500 mt-2">{error}</p>}
            <div className="mt-4 flex space-x-2">
              <button
                className="bg-purple-500 text-white px-4 py-2 rounded"
                onClick={() => {
                  setStartDate('');
                  setEndDate('');
                  setTrendType('SMA');
                  setTrendData(null);
                  setError('');
                }}
              >
                Clear
              </button>
              <button
                className={`bg-purple-500 text-white px-4 py-2 rounded ${!startDate || !endDate ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={handleDisplayClick}
                disabled={!startDate || !endDate}
              >
                Display
              </button>
            </div>
          </div>
          <div className="lg:col-span-2 bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-bold mb-4">Trend Prediction</h2>
            <div className="bg-gray-700 p-4 rounded-lg h-64">
              {chartData ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="total_revenue" stroke="#8884d8" />
                    {trendType === 'SMA' && (
                      <Line type="monotone" dataKey="sma_revenue" stroke="#82ca9d" />
                    )}
                    {trendType === 'EMA' && (
                      <Line type="monotone" dataKey="ema_revenue" stroke="#ffc658" />
                    )}
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <h2 className="text-5xl text-gray-400">Chart Placeholder</h2>
              )}
            </div>
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-8">
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-bold mb-4">Metric Explanation</h2>
            <p className="mb-4">
              <strong>Simple Moving Average (SMA)</strong>: The <strong>Simple Moving Average</strong> is a calculation that takes the unweighted mean of the previous n data points. It smooths out fluctuations in the data to help identify trends over a period of time. However, since all data points are treated equally, it might be slower to react to recent changes.
            </p>
            <p>
              <strong>Exponential Moving Average (EMA)</strong>: The <strong>Exponential Moving Average</strong> places a greater weight and significance on the most recent data points. This makes it more responsive to new information compared to the <strong>SMA</strong>. The <strong>EMA</strong> can help better capture trends and changes in the data more quickly.
            </p>
          </div>
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-bold mb-4">Trend Prediction Summary:</h2>
            <p>Trend Line: {trendType}</p>
            <p>Time Period: {startDate} to {endDate}</p>
            <p>Trend direction: {trendDirection}</p>
            <p>Peak of Actual Sales: {peakSalesMonth}</p>
            <p>Lowest Point of Actual Sales: {lowestSalesMonth}</p>
          </div>
        </div>
      </main>

      <footer className="mt-8 bg-gray-900 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-gray-400 flex justify-between">
          <p>Privacy Policy</p>
          <p>Terms of Service</p>
          <p>Cookies Settings</p>
        </div>
      </footer>
    </div>
  );
};

export default SalesAnalysisComponent;
