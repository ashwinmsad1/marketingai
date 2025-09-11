import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle, Clock, Lock } from 'lucide-react';

interface UsageBadgeProps {
  type: 'normal' | 'warning' | 'critical' | 'exceeded' | 'feature_locked';
  message: string;
  percentage?: number;
  className?: string;
  onClick?: () => void;
}

const UsageBadge: React.FC<UsageBadgeProps> = ({
  type,
  message,
  percentage,
  className = '',
  onClick
}) => {
  const getIcon = () => {
    switch (type) {
      case 'normal':
        return <CheckCircle className="h-4 w-4" />;
      case 'warning':
        return <Clock className="h-4 w-4" />;
      case 'critical':
      case 'exceeded':
        return <AlertTriangle className="h-4 w-4" />;
      case 'feature_locked':
        return <Lock className="h-4 w-4" />;
      default:
        return <CheckCircle className="h-4 w-4" />;
    }
  };

  const getStyles = () => {
    switch (type) {
      case 'normal':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          text: 'text-green-800',
          icon: 'text-green-600'
        };
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          text: 'text-yellow-800',
          icon: 'text-yellow-600'
        };
      case 'critical':
        return {
          bg: 'bg-orange-50',
          border: 'border-orange-200',
          text: 'text-orange-800',
          icon: 'text-orange-600'
        };
      case 'exceeded':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-800',
          icon: 'text-red-600'
        };
      case 'feature_locked':
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          text: 'text-gray-800',
          icon: 'text-gray-600'
        };
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          text: 'text-gray-800',
          icon: 'text-gray-600'
        };
    }
  };

  const styles = getStyles();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`
        inline-flex items-center space-x-2 px-3 py-2 rounded-lg border text-sm font-medium
        ${styles.bg} ${styles.border} ${styles.text}
        ${onClick ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}
        ${className}
      `}
      onClick={onClick}
    >
      <div className={styles.icon}>
        {getIcon()}
      </div>
      <span>{message}</span>
      {percentage !== undefined && (
        <span className="font-bold">
          {percentage.toFixed(0)}%
        </span>
      )}
    </motion.div>
  );
};

export default UsageBadge;