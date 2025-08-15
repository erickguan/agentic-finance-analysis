import React from 'react';
import { ChartBarIcon } from '@heroicons/react/24/outline';

const Header: React.FC = () => {
  return (
    <header className="bg-blue-600 shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center space-x-3">
          <ChartBarIcon className="h-8 w-8 text-white" />
          <div>
            <h1 className="text-2xl font-bold text-white">
              Financial Analysis AI
            </h1>
            <p className="text-blue-100 text-sm">
              Comprehensive stock analysis powered by AI agents
            </p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;