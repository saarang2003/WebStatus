import React from 'react';
import { Globe, BarChart3, Trash2 } from 'lucide-react';
import { getStatusIcon, getStatusColor } from '../utils/helpers';

function StatusItem({ status, onDelete, onViewAnalytics }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-lg transition-all duration-200 hover:border-slate-300">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
              <Globe className="w-5 h-5 text-slate-600" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 text-lg">{status.name}</h3>
              <p className="text-sm text-slate-500 break-all">{status.url}</p>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border text-sm font-medium ${getStatusColor(status.status)}`}>
              {getStatusIcon(status.status)}
              {status.status}
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => onViewAnalytics(status.name)}
                className="p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="View Analytics"
              >
                <BarChart3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => onDelete(status.name)}
                className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Delete website"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          {status.last_updated && (
            <div className="mt-3 text-xs text-slate-500">
              Last checked: {new Date(status.last_updated).toLocaleString()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default StatusItem;