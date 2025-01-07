'use client';

import React, { useEffect, useState, FC, useMemo } from 'react';
import SalesNav from '@/components/sales/SalesNav';
import { Label } from '../ui';
import { SalesAPI } from '@/services/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface SalesData {
  money: number;
  sales: number;
  sales_by_product: {
    productID__prodName: string;
    total_quantity: number;
    total_revenue: number;
  }[];
}

const SalesDashboard: FC = () => {
  const [data, setData] = useState<SalesData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<string>('today');

  const salesAPI = useMemo(() => new SalesAPI(), []);

  const fetchData = async (range: string) => {
    try {
      const response = await salesAPI.getSalesOverview(range);
      const responseData = response.data;

      console.log('Response Data:', responseData); // Log response data

      if (
        responseData.total_revenue !== undefined &&
        responseData.total_sales !== undefined
      ) {
        setData({
          money: parseFloat(responseData.total_revenue),
          sales: responseData.total_sales,
          sales_by_product: responseData.sales_by_product || [],
        });
      } else {
        setData({
          money: 0,
          sales: 0,
          sales_by_product: [],
        });
      }
    } catch (error: unknown) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError(String(error));
      }
    }
  };

  useEffect(() => {
    fetchData(dateRange);
  }, [dateRange, salesAPI]);

  const handleDateRangeChange = (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    setDateRange(event.target.value);
  };

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!data) {
    return <div>Loading...</div>;
  }

  console.log('Sales Data:', data.sales_by_product); // Log sales by product data

  const formattedMoney = data.money ? data.money.toLocaleString() : 'N/A';
  const formattedSales = data.sales ? data.sales.toLocaleString() : 'N/A';

  const chartData = data.sales_by_product.map((item) => ({
    product: item.productID__prodName,
    revenue: item.total_revenue,
    quantity: item.total_quantity,
  }));

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <SalesNav />
      <header className="bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-white">Sales Analysis</h1>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <label
            htmlFor="date-range"
            className="text-sm font-medium text-gray-400"
          >
            Select Date Range:{' '}
          </label>
          <select
            id="date-range"
            value={dateRange}
            onChange={handleDateRangeChange}
            className="ml-2 p-2 bg-gray-700 text-white rounded"
          >
            <option value="today">Today</option>
            <option value="7days">Last 7 Days</option>
            <option value="all">All Time</option>
          </select>
        </div>
        <div className="px-4 py-6 sm:px-0 grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-gray-800 overflow-hidden shadow rounded-lg p-4">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-400 truncate">
                <Label>Total Money</Label>
              </dt>
              <dd className="mt-1 text-3xl font-semibold text-white">
                ${formattedMoney}
              </dd>
            </div>
          </div>
          <div className="bg-gray-800 overflow-hidden shadow rounded-lg p-4">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-400 truncate">
                <Label>Total Sales</Label>
              </dt>
              <dd className="mt-1 text-3xl font-semibold text-white">
                {formattedSales}
              </dd>
            </div>
          </div>
        </div>
        <div className="mt-6 bg-gray-800 p-4 rounded-lg shadow-lg">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={chartData}
                margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#555" />
                <XAxis
                  dataKey="product"
                  stroke="#ddd"
                  interval={0}
                  angle={-45}
                  textAnchor="end"
                  tick={{ fontSize: 12, fontWeight: 'bold', fill: '#ddd' }}
                />
                <YAxis
                  stroke="#ddd"
                  tick={{ fontSize: 12, fontWeight: 'bold', fill: '#ddd' }}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#333', borderColor: '#777' }}
                />
                <Bar dataKey="revenue" fill="#8884d8" barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64">
              <span className="text-xl text-gray-400">No data available</span>
            </div>
          )}
          <div
            style={{ textAlign: 'center', marginTop: '20px', color: '#ddd' }}
          >
            <svg
              width="10"
              height="10"
              viewBox="0 0 32 32"
              style={{ display: 'inline-block', marginRight: 4 }}
            >
              <rect width="32" height="32" style={{ fill: '#8884d8' }} />
            </svg>
            Revenue
          </div>
        </div>
      </main>
    </div>
  );
};

export default SalesDashboard;
