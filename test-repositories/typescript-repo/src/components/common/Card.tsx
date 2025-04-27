import React from 'react';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  footer?: React.ReactNode;
  className?: string;
  padding?: 'none' | 'small' | 'medium' | 'large';
  shadow?: 'none' | 'small' | 'medium' | 'large';
  bordered?: boolean;
  rounded?: boolean;
}

/**
 * Reusable Card component for content containers
 */
const Card: React.FC<CardProps> = ({
  children,
  title,
  footer,
  className = '',
  padding = 'medium',
  shadow = 'medium',
  bordered = true,
  rounded = true,
}) => {
  // Padding classes
  const paddingClasses = {
    none: '',
    small: 'p-2',
    medium: 'p-4',
    large: 'p-6'
  };
  
  // Shadow classes
  const shadowClasses = {
    none: '',
    small: 'shadow-sm',
    medium: 'shadow',
    large: 'shadow-lg'
  };
  
  // Border and rounded classes
  const borderClass = bordered ? 'border border-gray-200' : '';
  const roundedClass = rounded ? 'rounded-lg' : '';
  
  // Combine all classes
  const cardClasses = `
    bg-white
    ${paddingClasses[padding]}
    ${shadowClasses[shadow]}
    ${borderClass}
    ${roundedClass}
    ${className}
  `;

  return (
    <div className={cardClasses}>
      {title && (
        <div className="mb-4 pb-2 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        </div>
      )}
      
      <div>{children}</div>
      
      {footer && (
        <div className="mt-4 pt-2 border-t border-gray-200">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card; 