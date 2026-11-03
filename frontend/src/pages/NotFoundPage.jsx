import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, FileQuestion } from 'lucide-react';
import Button from '../components/ui/Button';

export default function NotFoundPage() {
  return (
    <div className="py-24 text-center max-w-md mx-auto space-y-4">
      <FileQuestion className="w-12 h-12 mx-auto text-slate-400" />
      <h1 className="text-xl font-bold text-slate-900">Page Not Found</h1>
      <p className="text-xs text-slate-600">The requested learning unit or workspace route does not exist.</p>
      <Link to="/">
        <Button variant="primary" size="sm" icon={ArrowLeft}>
          Return to Dashboard
        </Button>
      </Link>
    </div>
  );
}

