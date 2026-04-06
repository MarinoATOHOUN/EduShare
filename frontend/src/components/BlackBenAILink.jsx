import React from 'react';

const BlackBenAILink = ({ className = '', children = 'BlackBenAI' }) => {
  return (
    <a
      href="https://blackbenai.com"
      target="_blank"
      rel="noopener noreferrer"
      className={`font-semibold text-foreground hover:text-primary hover:underline underline-offset-4 ${className}`}
    >
      {children}
    </a>
  );
};

export default BlackBenAILink;
