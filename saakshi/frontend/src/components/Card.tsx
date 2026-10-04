import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  action?: React.ReactNode;
}

export function Card({ children, className = '', title, action }: CardProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-surface border border-border rounded-xl overflow-hidden flex flex-col ${className}`}
    >
      {(title || action) && (
        <div className="px-6 py-4 border-b border-border flex items-center justify-between shrink-0 bg-white/[0.02]">
          {title && <h3 className="font-semibold tracking-wide text-text">{title}</h3>}
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-6 flex-1 flex flex-col min-h-0 overflow-auto">
        {children}
      </div>
    </motion.div>
  );
}
