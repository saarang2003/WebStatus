import React from 'react';
import { RefreshCw, Home, Plus, Monitor } from 'lucide-react';
import StatusItem from './StatusItem';

function Dashboard({ 
  stats, globalStats, statusList, name, url, setName, setUrl, 
  error, isLoading, addStatusHandler, deleteStatusHandler, 
  viewAnalyticsHandler, fetchStatuses, setCurrentView 
}) {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="bg-white border border-slate-200 rounded-xl p-6 mb-8 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Website Monitoring Dashboard</h1>
              <p className="text-slate-600">Real-time status monitoring and analytics</p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={fetchStatuses}
                className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                title="Refresh"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
              <button
                onClick={() => setCurrentView('landing')}
                className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 text-sm font-medium"
              >
                <Home className="w-4 h-4" />
                Home
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-slate-900">{stats.total}</div>
              <div className="text-sm text-slate-600">Total Websites</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{stats.up}</div>
              <div className="text-sm text-slate-600">Online</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600">{stats.down}</div>
              <div className="text-sm text-slate-600">Offline</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {globalStats?.checks_last_24h || 0}
              </div>
              <div className="text-sm text-slate-600">Checks (24h)</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          <div className="xl:col-span-1">
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm mb-8">
              <div className="flex items-center gap-2 mb-6">
                <Plus className="w-5 h-5 text-slate-600" />
                <h2 className="text-xl font-semibold text-slate-900">Add Website</h2>
              </div>
              
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
                  {error}
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Website Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g., My Website"
                    className="w-full px-4 py-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent bg-slate-50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Website URL</label>
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://example.com"
                    className="w-full px-4 py-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent bg-slate-50 font-mono text-sm"
                  />
                </div>
                <button
                  onClick={addStatusHandler}
                  disabled={isLoading}
                  className="w-full bg-black text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Adding...' : 'Add Website'}
                </button>
                <p className="text-xs text-slate-500 text-center">
                  Monitoring checks run every 2 minutes
                </p>
              </div>
            </div>
          </div>

          <div className="xl:col-span-2">
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
              <div className="flex items-center gap-2 mb-6">
                <Monitor className="w-5 h-5 text-slate-600" />
                <h2 className="text-xl font-semibold text-slate-900">Monitored Websites</h2>
              </div>
              
              {statusList.length === 0 ? (
                <div className="text-center py-12">
                  <Monitor className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-slate-900 mb-2">No websites monitored</h3>
                  <p className="text-slate-600">Add your first website to start monitoring</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {statusList.map((status, index) => (
                    <StatusItem 
                      key={index} 
                      status={status} 
                      onDelete={deleteStatusHandler}
                      onViewAnalytics={viewAnalyticsHandler}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;