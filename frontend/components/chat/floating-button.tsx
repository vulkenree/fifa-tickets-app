'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { MessageSquare, Sparkles } from 'lucide-react';

export function FloatingChatButton() {
  const [isHovered, setIsHovered] = useState(false);
  const router = useRouter();

  const handleClick = () => {
    router.push('/chat');
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Button
        onClick={handleClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="h-14 w-14 rounded-full bg-blue-500 hover:bg-blue-600 text-white shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center group"
        size="lg"
      >
        {isHovered ? (
          <div className="flex items-center space-x-2">
            <Sparkles size={20} />
            <span className="text-sm font-medium">AI Assistant</span>
          </div>
        ) : (
          <MessageSquare size={24} />
        )}
      </Button>
    </div>
  );
}
