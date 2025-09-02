import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Target,
  BarChart3,
  Palette,
  Facebook,
  Settings,
  ChevronLeft,
  ChevronRight,
  HelpCircle,
  CreditCard,
} from 'lucide-react';
import { cn } from '../../utils/cn';

// Types for navigation items
interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<any>;
  path?: string;
  items?: SubNavItem[];
  badge?: string | number;
}

interface SubNavItem {
  id: string;
  label: string;
  path: string;
  badge?: string | number;
  description?: string;
}

// Primary navigation items
const primaryNavItems: NavItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    path: '/dashboard',
  },
  {
    id: 'campaigns',
    label: 'Campaigns',
    icon: Target,
    items: [
      {
        id: 'campaigns-list',
        label: 'My Campaigns',
        path: '/campaigns',
        description: 'View and manage your campaigns',
      },
      {
        id: 'create-campaign',
        label: 'Create Campaign',
        path: '/create-campaign',
        description: 'Launch a new marketing campaign',
      },
    ],
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: BarChart3,
    path: '/analytics',
  },
  {
    id: 'media',
    label: 'Media Creation',
    icon: Palette,
    items: [
      {
        id: 'media-create',
        label: 'Create Content',
        path: '/media-creation',
        description: 'Generate images and videos with AI',
      },
      {
        id: 'media-library',
        label: 'Media Library',
        path: '/media-library',
        description: 'Browse your created assets',
      },
    ],
  },
  {
    id: 'integrations',
    label: 'Integrations',
    icon: Facebook,
    items: [
      {
        id: 'meta-connect',
        label: 'Connect Meta',
        path: '/meta/connect',
        description: 'Connect your Facebook/Instagram accounts',
      },
      {
        id: 'meta-accounts',
        label: 'Meta Accounts',
        path: '/meta/accounts',
        description: 'Manage connected Meta accounts',
      },
    ],
  },
];

// Bottom navigation items
const bottomNavItems: NavItem[] = [
  {
    id: 'billing',
    label: 'Subscription',
    icon: CreditCard,
    items: [
      {
        id: 'subscription',
        label: 'Subscription',
        path: '/subscription',
        description: 'Manage your subscription plan',
      },
      {
        id: 'billing-history',
        label: 'Billing History',
        path: '/billing/history',
        description: 'View payment history and invoices',
      },
    ],
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    path: '/settings',
  },
  {
    id: 'help',
    label: 'Help & Support',
    icon: HelpCircle,
    path: '/help',
  },
];

interface DualSidebarProps {
  children: React.ReactNode;
  className?: string;
}

export const DualSidebar: React.FC<DualSidebarProps> = ({ children, className }) => {
  const [primaryCollapsed, setPrimaryCollapsed] = useState(false);
  const [secondaryVisible, setSecondaryVisible] = useState(true);
  const [activeItem, setActiveItem] = useState<string>('dashboard');
  const [isMobile, setIsMobile] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Handle mobile detection
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
      if (window.innerWidth < 1024) {
        setPrimaryCollapsed(true);
        setSecondaryVisible(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Update active item based on current route
  useEffect(() => {
    const currentPath = location.pathname;
    const item = primaryNavItems.find(item => 
      item.path === currentPath || 
      item.items?.some(subItem => subItem.path === currentPath)
    );
    
    if (item) {
      setActiveItem(item.id);
    }
  }, [location]);

  // Get current secondary items
  const getCurrentSecondaryItems = (): SubNavItem[] => {
    const currentItem = primaryNavItems.find(item => item.id === activeItem);
    return currentItem?.items || [];
  };

  // Handle navigation
  const handleNavigation = (item: NavItem) => {
    setActiveItem(item.id);
    
    if (item.path) {
      navigate(item.path);
    } else if (item.items && item.items.length > 0) {
      // If has subitems, navigate to first subitem
      navigate(item.items[0].path);
    }
    
    // Show secondary sidebar if item has subitems
    if (item.items && item.items.length > 0 && !isMobile) {
      setSecondaryVisible(true);
    } else if (!isMobile) {
      setSecondaryVisible(false);
    }
  };

  const handleSubNavigation = (subItem: SubNavItem) => {
    navigate(subItem.path);
  };

  const currentSecondaryItems = getCurrentSecondaryItems();
  const showSecondary = secondaryVisible && currentSecondaryItems.length > 0 && !isMobile;

  return (
    <div className={cn('flex h-screen bg-gray-50', className)}>
      {/* Primary Sidebar */}
      <div
        className={cn(
          'bg-white border-r border-gray-200 shadow-sm transition-all duration-300 z-50',
          primaryCollapsed ? 'w-16' : 'w-64',
          isMobile && 'fixed inset-y-0 left-0'
        )}
      >
        {/* Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-100">
          {!primaryCollapsed && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <span className="font-semibold text-gray-900">MarketingAI</span>
            </div>
          )}
          <button
            onClick={() => setPrimaryCollapsed(!primaryCollapsed)}
            className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors"
          >
            {primaryCollapsed ? (
              <ChevronRight className="w-5 h-5" />
            ) : (
              <ChevronLeft className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 flex flex-col justify-between py-4">
          <nav className="space-y-1 px-2">
            {primaryNavItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleNavigation(item)}
                className={cn(
                  'w-full flex items-center text-left rounded-lg transition-colors group relative',
                  primaryCollapsed ? 'p-3 justify-center' : 'p-3 space-x-3',
                  activeItem === item.id
                    ? 'bg-blue-50 text-blue-700 border-blue-200'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                )}
              >
                <item.icon
                  className={cn(
                    'w-5 h-5 flex-shrink-0',
                    activeItem === item.id ? 'text-blue-600' : 'text-gray-500'
                  )}
                />
                {!primaryCollapsed && (
                  <>
                    <span className="font-medium">{item.label}</span>
                    {item.badge && (
                      <span className="ml-auto bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
                
                {/* Tooltip for collapsed state */}
                {primaryCollapsed && (
                  <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                    {item.label}
                  </div>
                )}
              </button>
            ))}
          </nav>

          {/* Bottom Navigation */}
          <nav className="space-y-1 px-2 border-t border-gray-100 pt-4">
            {bottomNavItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleNavigation(item)}
                className={cn(
                  'w-full flex items-center text-left rounded-lg transition-colors group relative',
                  primaryCollapsed ? 'p-3 justify-center' : 'p-3 space-x-3',
                  'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                )}
              >
                <item.icon className="w-5 h-5 flex-shrink-0 text-gray-500" />
                {!primaryCollapsed && <span className="font-medium">{item.label}</span>}
                
                {primaryCollapsed && (
                  <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                    {item.label}
                  </div>
                )}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Secondary Sidebar */}
      {showSecondary && (
        <div className="w-80 bg-gray-50 border-r border-gray-200">
          <div className="h-16 flex items-center justify-between px-6 border-b border-gray-200 bg-white">
            <h2 className="font-semibold text-gray-900">
              {primaryNavItems.find(item => item.id === activeItem)?.label}
            </h2>
            <button
              onClick={() => setSecondaryVisible(false)}
              className="p-1 rounded hover:bg-gray-100 text-gray-500"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
          </div>
          
          <div className="p-4">
            <nav className="space-y-2">
              {currentSecondaryItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleSubNavigation(item)}
                  className={cn(
                    'w-full text-left p-4 rounded-lg transition-colors border',
                    location.pathname === item.path
                      ? 'bg-white border-blue-200 shadow-sm ring-1 ring-blue-100'
                      : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-sm'
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{item.label}</div>
                      {item.description && (
                        <div className="text-sm text-gray-500 mt-1">{item.description}</div>
                      )}
                    </div>
                    {item.badge && (
                      <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full ml-2">
                        {item.badge}
                      </span>
                    )}
                  </div>
                </button>
              ))}
            </nav>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {children}
      </div>

      {/* Mobile overlay */}
      {isMobile && !primaryCollapsed && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setPrimaryCollapsed(true)}
        />
      )}
    </div>
  );
};

export default DualSidebar;