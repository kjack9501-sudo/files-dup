import React, { useRef, useEffect, useState } from 'react';

interface CustomScrollbarProps {
  children: React.ReactNode;
  className?: string;
}

const CustomScrollbar: React.FC<CustomScrollbarProps> = ({ children, className = '' }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const thumbRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [thumbWidth, setThumbWidth] = useState(0);
  const [thumbLeft, setThumbLeft] = useState(0);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const updateScrollbar = () => {
      const { scrollWidth, clientWidth, scrollLeft } = container;
      const scrollRatio = clientWidth / scrollWidth;
      const newThumbWidth = Math.max(20, scrollRatio * clientWidth);
      const maxScroll = scrollWidth - clientWidth;
      const scrollRatio2 = maxScroll > 0 ? scrollLeft / maxScroll : 0;
      const maxThumbLeft = clientWidth - newThumbWidth;
      const newThumbLeft = scrollRatio2 * maxThumbLeft;

      setThumbWidth(newThumbWidth);
      setThumbLeft(newThumbLeft);
    };

    updateScrollbar();
    container.addEventListener('scroll', updateScrollbar);
    window.addEventListener('resize', updateScrollbar);

    return () => {
      container.removeEventListener('scroll', updateScrollbar);
      window.removeEventListener('resize', updateScrollbar);
    };
  }, []);

  const handleThumbMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !containerRef.current || !thumbRef.current) return;

      const container = containerRef.current;
      const containerRect = container.getBoundingClientRect();
      const containerWidth = container.clientWidth;
      const maxThumbLeft = containerWidth - thumbWidth;
      
      let newThumbLeft = e.clientX - containerRect.left - (thumbWidth / 2);
      newThumbLeft = Math.max(0, Math.min(maxThumbLeft, newThumbLeft));
      
      const scrollRatio = newThumbLeft / maxThumbLeft;
      const maxScroll = container.scrollWidth - container.clientWidth;
      container.scrollLeft = scrollRatio * maxScroll;
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, thumbWidth]);

  return (
    <div className={`relative ${className}`}>
      <div
        ref={containerRef}
        className="overflow-x-auto"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        <style>{`
          .overflow-x-auto::-webkit-scrollbar {
            display: none;
          }
        `}</style>
        {children}
      </div>
      {containerRef.current && containerRef.current.scrollWidth > containerRef.current.clientWidth && (
        <div className="h-1 bg-gray-200 rounded-full mt-1 relative">
          <div
            ref={thumbRef}
            className="h-1 bg-blue-500 rounded-full cursor-pointer"
            style={{
              width: `${thumbWidth}px`,
              left: `${thumbLeft}px`,
            }}
            onMouseDown={handleThumbMouseDown}
          />
        </div>
      )}
    </div>
  );
};

export default CustomScrollbar;

