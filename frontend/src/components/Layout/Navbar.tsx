import React, { useState } from 'react';
import { Menu, X, User, Bell, Settings, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface NavbarProps {
  user: {
    name: string;
    subscription_tier: string;
  };
  onNavigate: (page: string) => void;
  currentPage: string;
}

const Navbar: React.FC<NavbarProps> = ({ user, onNavigate, currentPage }) => {
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', href: 'dashboard' },
    { id: 'create-campaign', label: 'Create Campaign', href: 'create-campaign' },
    { id: 'media-creation', label: 'Create Content', href: 'media-creation' },
    { id: 'campaigns', label: 'My Campaigns', href: 'campaigns' },
    { id: 'analytics', label: 'Analytics', href: 'analytics' }
  ];

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <button
                onClick={() => onNavigate('dashboard')}
                className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent hover:opacity-80 transition-opacity duration-200"
              >
                AIMarketing
              </button>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.href)}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    currentPage === item.href
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {/* Right side items */}
          <div className="hidden md:flex items-center space-x-4">
            {/* Notifications */}
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              <Bell className="w-5 h-5" />
            </button>

            {/* Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="flex items-center space-x-3 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-gray-900">{user.name}</p>
                  <p className="text-xs text-gray-500 capitalize">{user.subscription_tier}</p>
                </div>
              </button>

              <AnimatePresence>
                {isProfileOpen && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    transition={{ duration: 0.1 }}
                    className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50"
                  >
                    <button
                      onClick={() => {
                        onNavigate('settings');
                        setIsProfileOpen(false);
                      }}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <Settings className="w-4 h-4 mr-3" />
                      Settings
                    </button>
                    <button
                      onClick={() => {
                        onNavigate('landing');
                        setIsProfileOpen(false);
                      }}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <LogOut className="w-4 h-4 mr-3" />
                      Sign Out
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
            >
              {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden bg-white border-t border-gray-200"
          >
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    onNavigate(item.href);
                    setIsMobileMenuOpen(false);
                  }}
                  className={`block w-full text-left px-3 py-2 rounded-md text-base font-medium transition-colors ${
                    currentPage === item.href
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
            
            <div className="pt-4 pb-3 border-t border-gray-200">
              <div className="flex items-center px-5">
                <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-white" />
                </div>
                <div className="ml-3">
                  <div className="text-base font-medium text-gray-800">{user.name}</div>
                  <div className="text-sm text-gray-500 capitalize">{user.subscription_tier} Plan</div>
                </div>
              </div>
              <div className="mt-3 px-2 space-y-1">
                <button
                  onClick={() => {
                    onNavigate('settings');
                    setIsMobileMenuOpen(false);
                  }}
                  className="flex items-center w-full px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
                >
                  <Settings className="w-5 h-5 mr-3" />
                  Settings
                </button>
                <button
                  onClick={() => {
                    onNavigate('landing');
                    setIsMobileMenuOpen(false);
                  }}
                  className="flex items-center w-full px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
                >
                  <LogOut className="w-5 h-5 mr-3" />
                  Sign Out
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;