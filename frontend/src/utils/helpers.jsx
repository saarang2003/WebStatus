import { CheckCircle, XCircle, Clock } from 'lucide-react';

export const getStatusIcon = (statusValue) => {
  switch (statusValue) {
    case 'UP':
      return < CheckCircle className="w-5 h-5 text-green-500" />;
    case 'Down':
      return < XCircle className="w-5 h-5 text-red-500" />;
    default:
      return < Clock className="w-5 h-5 text-yellow-500 animate-spin" />;
  }
};

export const getStatusColor = (statusValue) => {
  switch (statusValue) {
    case 'UP':
      return 'text-green-700 bg-green-50 border-green-200';
    case 'Down':
      return 'text-red-700 bg-red-50 border-red-200';
    default:
      return 'text-yellow-700 bg-yellow-50 border-yellow-200';
  }
};