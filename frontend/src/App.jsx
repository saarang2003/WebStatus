/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from 'react';
import { Globe, Activity, Clock, BarChart3, Trash2, RefreshCw, Plus, TrendingUp } from 'lucide-react';

function App() {
  const [websites, setWebsites] = useState([]);
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({ total_websites: 0, websites_up: 0, websites_down: 0, average_response_time: 0 });

  // Fetch all websites
  const fetchWebsites = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/websites');
      if (response.ok) {
        const data = await response.json();
        setWebsites(data);
      }
    } catch (error) {
      console.error('Error fetching websites:', error);
    }
  };

  // Fetch stats
  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // Add new website
  const addWebsite = async () => {
    if (!name.trim() || !url.trim()) {
      setError('Please fill in both name and URL');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/websites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), url: url.trim() })
      });

      if (response.ok) {
        setName('');
        setUrl('');
        await fetchWebsites();
        await fetchStats();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to add website');
      }
    } catch (error) {
      setError('Failed to add website. Make sure the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  // Delete website
  const deleteWebsite = async (name) => {
    try {
      const response = await fetch(`http://localhost:8000/api/websites/${name}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        await fetchWebsites();
        await fetchStats();
      }
    } catch (error) {
      console.error('Error deleting website:', error);
    }
  };

  // Re-check a specific website
  const recheckWebsite = async (name) => {
    try {
      const response = await fetch(`http://localhost:8000/api/check/${name}`);
      if (response.ok) {
        await fetchWebsites();
        await fetchStats();
      }
    } catch (error) {
      console.error('Error rechecking website:', error);
    }
  };

  // Check all websites
  const checkAllWebsites = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/check-all', {
        method: 'POST'
      });
      if (response.ok) {
        await fetchWebsites();
        await fetchStats();
      }
    } catch (error) {
      console.error('Error checking all websites:', error);
    }
  };

  useEffect(() => {
    fetchWebsites();
    fetchStats();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchWebsites();
      fetchStats();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    if (status === 'UP') return 'bg-green-50 border-green-200 text-green-700';
    if (status === 'DOWN') return 'bg-red-50 border-red-200 text-red-700';
    return 'bg-yellow-50 border-yellow-200 text-yellow-700';
  };

  const getStatusIcon = (status) => {
    if (status === 'UP') return <div className="w-2 h-2 bg-green-500 rounded-full"></div>;
    if (status === 'DOWN') return <div className="w-2 h-2 bg-red-500 rounded-full"></div>;
    return <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>;
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-6xl mx-auto px-6 py-8">
        
        {/* Header */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 mb-8 shadow-sm">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Website Monitor</h1>
          <p className="text-slate-600">Monitor website status, response time, and traffic</p>
          
          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="text-center p-4 bg-slate-50 rounded-lg">
              <div className="text-2xl font-bold text-slate-900">{stats.total_websites}</div>
              <div className="text-sm text-slate-600">Total Sites</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{stats.websites_up}</div>
              <div className="text-sm text-slate-600">Online</div>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{stats.websites_down}</div>
              <div className="text-sm text-slate-600">Offline</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{stats.average_response_time}s</div>
              <div className="text-sm text-slate-600">Avg Response</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Add Website Form */}
          <div className="lg:col-span-1">
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
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
                    placeholder="e.g., Google"
                    className="w-full px-4 py-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Website URL</label>
                  <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="google.com or https://google.com"
                    className="w-full px-4 py-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                  />
                </div>
                <button
                  onClick={addWebsite}
                  disabled={isLoading}
                  className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Adding...' : 'Add Website'}
                </button>
              </div>
            </div>
          </div>

          {/* Websites List */}
          <div className="lg:col-span-2">
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-slate-600" />
                  <h2 className="text-xl font-semibold text-slate-900">Monitored Websites</h2>
                </div>
                <button
                  onClick={checkAllWebsites}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  Check All
                </button>
              </div>
              
              {websites.length === 0 ? (
                <div className="text-center py-12">
                  <Globe className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-slate-900 mb-2">No websites added yet</h3>
                  <p className="text-slate-600">Add your first website to start monitoring</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {websites.map((website) => (
                    <div key={website.name} className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      
                      {/* Website Header */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
                            <Globe className="w-5 h-5 text-slate-600" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-slate-900">{website.name}</h3>
                            <p className="text-sm text-slate-500 break-all">{website.url}</p>
                          </div>
                        </div>
                        
                        <div className="flex gap-2">
                          <button
                            onClick={() => recheckWebsite(website.name)}
                            className="p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Re-check"
                          >
                            <RefreshCw className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => deleteWebsite(website.name)}
                            className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      {/* Status & Metrics */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        
                        {/* Status */}
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-slate-600">Status:</span>
                          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(website.status)}`}>
                            {getStatusIcon(website.status)}
                            {website.status}
                          </div>
                        </div>

                        {/* Response Time */}
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-slate-600">Response:</span>
                          <div className="inline-flex items-center gap-2 text-sm">
                            <Clock className="w-4 h-4 text-blue-500" />
                            <span className="font-medium">{website.response_time}s</span>
                          </div>
                        </div>

                        {/* Status Code */}
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-slate-600">Code:</span>
                          <span className="text-sm font-medium text-slate-900">
                            {website.status_code || 'N/A'}
                          </span>
                        </div>
                      </div>

                      {/* Traffic Info */}
                      <div className="mt-3 p-3 bg-slate-50 rounded-lg">
                        <div className="flex items-center gap-2">
                          <TrendingUp className="w-4 h-4 text-slate-500" />
                          <span className="text-sm font-medium text-slate-700">Traffic Analysis:</span>
                        </div>
                        <p className="text-sm text-slate-600 mt-1">{website.traffic_info}</p>
                      </div>

                      {/* Last Checked */}
                      <div className="mt-3 text-xs text-slate-500">
                        Last checked: {website.last_checked}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Simple Analytics Chart */}
        {websites.length > 0 && (
          <div className="mt-8 bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Quick Overview</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Response Time Chart */}
              <div>
                <h4 className="text-sm font-medium text-slate-700 mb-3">Response Times</h4>
                <div className="space-y-2">
                  {websites.map((website) => (
                    <div key={website.name} className="flex items-center justify-between p-2 bg-slate-50 rounded">
                      <span className="text-sm text-slate-700">{website.name}</span>
                      <div className="flex items-center gap-2">
                        <div 
                          className="h-2 bg-blue-500 rounded"
                          style={{ width: `${Math.min(website.response_time * 20, 100)}px` }}
                        ></div>
                        <span className="text-sm font-medium text-slate-900">{website.response_time}s</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Status Overview */}
              <div>
                <h4 className="text-sm font-medium text-slate-700 mb-3">Status Summary</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Online Websites</span>
                    <span className="text-lg font-bold text-green-600">{stats.websites_up}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Offline Websites</span>
                    <span className="text-lg font-bold text-red-600">{stats.websites_down}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Average Response</span>
                    <span className="text-lg font-bold text-blue-600">{stats.average_response_time}s</span>
                  </div>
                  
                  {/* Simple uptime percentage */}
                  <div className="mt-4 p-3 bg-slate-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-slate-600">Overall Status</span>
                      <span className="text-sm font-medium text-slate-900">
                        {stats.total_websites > 0 ? Math.round((stats.websites_up / stats.total_websites) * 100) : 0}% UP
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full transition-all duration-300"
                        style={{ 
                          width: `${stats.total_websites > 0 ? (stats.websites_up / stats.total_websites) * 100 : 0}%` 
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-slate-500">
          <p>Auto-refreshes every 30 seconds • Backend: http://localhost:8000</p>
        </div>
      </div>
    </div>
  );
}

export default App;