import React from 'react';
import { Outlet } from 'react-router-dom';
import { DualSidebar } from '../components/Navigation/DualSidebar';
import { cn } from '../utils/cn';

interface AppLayoutProps {
  children?: React.ReactNode;
  className?: string;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children, className }) => {
  return (
    <div className={cn('min-h-screen bg-gray-50', className)}>
      <DualSidebar>
        {/* Top Bar */}
        <header className="h-16 bg-white border-b border-gray-200 shadow-sm">
          <div className="h-full flex items-center justify-between px-6">
            {/* Breadcrumbs or Page Title will go here */}
            <div className="flex items-center space-x-4">
              <div className="text-lg font-semibold text-gray-900">
                {/* This will be dynamically populated */}
              </div>
            </div>

            {/* Top Right Actions */}
            <div className="flex items-center space-x-4">
              {/* Notifications, user menu, etc. will go here */}
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto">
          <div className="p-6">
            {children || <Outlet />}
          </div>
        </main>
      </DualSidebar>
    </div>
  );
};

export default AppLayout;