'use client';

import React, { useEffect, useState, useRef } from 'react';
import { SalesAPI, API } from '../../services/api';
import { Progress, Card, Button, Select } from 'flowbite-react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { saveAs } from 'file-saver';
import Cookies from 'js-cookie';
import clearAllCookies from '@/services/clearCookies';

interface Report {
  reportID: number;
  reportName: string;
  description: string;
  createdDate: string;
  createdBy: string;
}

const GenerateReportComponent: React.FC = () => {
  const [reportTemplate, setReportTemplate] = useState('product-analysis');
  const [fromDate, setFromDate] = useState<Date | null>(null);
  const [toDate, setToDate] = useState<Date | null>(null);
  const [loading, setLoading] = useState(false);
  const [generatedReports, setGeneratedReports] = useState<Report[]>([]);
  const [userName, setUserName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const email = Cookies.get('email') || '';

  const apiRef = useRef(new API());

  useEffect(() => {
    const fetchUserName = async () => {
      try {
        if (email === '') {
          clearAllCookies();
          window.location.replace('/');
          return;
        }
        const response = await apiRef.current.post('get-username/', {
          email: email,
        });
        if (response.status === 200) {
          setUserName(response.data.username);
        } else {
          setError('Failed to fetch user data');
        }
      } catch (err) {
        setError('Failed to fetch user data');
      }
    };

    const fetchExistingReports = async () => {
      try {
        const response = await apiRef.current.get('sales/reports/');
        if (response.status === 200) {
          setGeneratedReports(response.data);
        } else {
          setError('Failed to fetch reports data');
        }
      } catch (err) {
        setError('Failed to fetch reports data');
      }
    };

    fetchUserName();
    fetchExistingReports();
  }, [email]);

  const handleGenerateReport = async () => {
    if (!fromDate || !toDate) {
      setError('Please select both From and To dates.');
      return;
    }

    setLoading(true);
    try {
      const response = await new SalesAPI().generateSalesPerformanceReport({
        fromDate: fromDate ? fromDate.toISOString().split('T')[0] : null,
        toDate: toDate ? toDate.toISOString().split('T')[0] : null,
        reportType: reportTemplate
      });
      if (response.status === 200) {
        const blob = new Blob([response.data]);
        saveAs(blob, `${reportTemplate}_report.csv`);

        // Save the report details to the database
        const reportData = {
          reportID: Math.floor(Math.random() * 1000), // Random ID for demonstration
          reportName: reportTemplate === 'product-analysis' ? 'Product Analysis' : 'Sales Summary',
          description: 'Description',
          createdDate: new Date().toISOString().split('T')[0], // Current date in YYYY-MM-DD format
          createdBy: userName || 'Unknown',
        };

        await apiRef.current.post('sales/create-report/', reportData);

        setGeneratedReports([
          ...generatedReports,
          {
            reportID: reportData.reportID,
            reportName: reportData.reportName,
            description: reportData.description,
            createdDate: reportData.createdDate,
            createdBy: reportData.createdBy,
          },
        ]);
      } else {
        setError('Failed to generate report.');
      }
    } catch (error) {
      console.error('Error generating report:', error);
      setError('Failed to generate report.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteReport = async (id: number) => {
    try {
      await apiRef.current.delete(`sales/reports/${id}/`);
      setGeneratedReports(generatedReports.filter((report) => report.reportID !== id));
    } catch (error) {
      console.error('Error deleting report:', error);
    }
  };

  return (
    <div className="container mx-auto p-6 bg-gray-900 text-white">
      <h1 className="text-4xl font-bold mb-4">Generate Report</h1>
      <Card className="mb-6 bg-gray-800 text-white p-6 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="template" className="block mb-2 text-sm font-medium text-gray-300">
              Report Template
            </label>
            <Select
              id="template"
              required
              value={reportTemplate}
              onChange={(e) => setReportTemplate(e.target.value)}
              className="bg-gray-700 text-white p-2 rounded"
            >
              <option value="product-analysis">Product Analysis</option>
              <option value="sales-summary">Sales Summary</option>
            </Select>
          </div>
          <div>
            <h2 className="text-lg font-medium text-gray-300 mb-2">Report Parameters</h2>
            <div className="flex flex-col md:flex-row md:space-x-4">
              <div className="flex flex-col mb-4 md:mb-0">
                <label htmlFor="fromDate" className="block mb-2 text-sm font-medium text-gray-300">
                  From
                </label>
                <DatePicker
                  id="fromDate"
                  selected={fromDate}
                  onChange={(date: Date | null) => setFromDate(date)}
                  className="text-black bg-gray-700 text-white p-2 rounded"
                  wrapperClassName="bg-gray-700"
                />
              </div>
              <div className="flex flex-col">
                <label htmlFor="toDate" className="block mb-2 text-sm font-medium text-gray-300">
                  To
                </label>
                <DatePicker
                  id="toDate"
                  selected={toDate}
                  onChange={(date: Date | null) => setToDate(date)}
                  className="text-black bg-gray-700 text-white p-2 rounded"
                  wrapperClassName="bg-gray-700"
                />
              </div>
            </div>
            {error && <p className="text-red-500 mt-2">{error}</p>}
          </div>
          <div className="flex justify-end space-x-4 mt-4">
            <Button
              onClick={() => {
                setReportTemplate('');
                setFromDate(null);
                setToDate(null);
                setError(null);
              }}
              className="bg-purple-600 hover:bg-purple-700 text-white p-2 rounded"
            >
              Clear
            </Button>
            <Button onClick={handleGenerateReport} className="bg-purple-600 hover:bg-purple-700 text-white p-2 rounded">
              {loading ? <Progress progress={0} /> : 'Generate'}
            </Button>
          </div>
        </div>
      </Card>
      <h2 className="text-3xl font-bold mb-4">Generated Reports</h2>
      <Card className="bg-gray-800 text-white p-6 rounded-lg shadow">
        <table className="min-w-full bg-gray-800 text-white">
          <thead>
            <tr>
              <th className="px-4 py-2 text-left">Report ID</th>
              <th className="px-4 py-2 text-left">Report Name</th>
              <th className="px-4 py-2 text-left">Description</th>
              <th className="px-4 py-2 text-left">Date</th>
              <th className="px-4 py-2 text-left">Created by</th>
              <th className="px-4 py-2 text-left">Action</th>
            </tr>
          </thead>
          <tbody>
            {generatedReports.map((report) => (
              <tr key={report.reportID} className="bg-gray-700 text-white">
                <td className="border px-4 py-2">{report.reportID}</td>
                <td className="border px-4 py-2">{report.reportName}</td>
                <td className="border px-4 py-2">{report.description}</td>
                <td className="border px-4 py-2">{report.createdDate}</td>
                <td className="border px-4 py-2">{report.createdBy}</td>
                <td className="border px-4 py-2">
                  <Button
                    size="xs"
                    color="red"
                    onClick={() => handleDeleteReport(report.reportID)}
                    className="bg-red-600 hover:bg-red-700 text-white p-1 rounded"
                  >
                    Delete
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
};

export default GenerateReportComponent;
