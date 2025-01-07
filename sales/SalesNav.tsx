import Link from 'next/link';

const SalesNav = () => {
  return (
    <nav className="bg-slate-700 text-white p-2">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex space-x-4">
          <Link href="/sales" className="hover:text-gray-300">
            Overview
          </Link>
          <Link href="/sales/generate-report" className="hover:text-gray-300">
            Generate Report
          </Link>
          <Link href="/sales/salesanalysis" className="hover:text-gray-300">
            Sales Analysis
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default SalesNav;
