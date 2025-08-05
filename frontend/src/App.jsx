import React, { useState, useEffect } from 'react';
import { 
  Monitor, Globe, CheckCircle, XCircle, Clock, Plus, Trash2, Activity, 
  Users, Zap, TrendingUp, AlertTriangle, BarChart3, PieChart, 
  RefreshCw, Calendar, Download, Bell, Settings, Home, ArrowLeft
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Cell, BarChart, Bar, Pie } from 'recharts';

// Color palette
const COLORS = ['#10b981', '#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6'];

// StatusItem Component with Enhanced Analytics
function StatusItem({ status, onDelete, onViewAnalytics }) {
  const getStatusIcon = (statusValue) => {
    switch (statusValue) {
      case 'UP':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'Down':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-500 animate-spin" />;
    }
  };

  const getStatusColor = (statusValue) => {
    switch (statusValue) {
      case 'UP':
        return 'text-green-700 bg-green-50 border-green-200';
      case 'Down':
        return 'text-red-700 bg-red-50 border-red-200';
      default:
        return 'text-yellow-700 bg-yellow-50 border-yellow-200';
    }
  };

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

// Analytics Dashboard Component
function AnalyticsDashboard({ websiteName, onBack }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(24);

  useEffect(() => {
    fetchAnalytics();
  }, [websiteName, timeRange]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/analytics/${websiteName}/complete?hours=${timeRange}`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-slate-400 animate-spin mx-auto mb-4" />
          <p className="text-slate-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-4" />
          <p className="text-slate-600">Failed to load analytics data</p>
          <button onClick={onBack} className="mt-4 text-blue-600 hover:text-blue-800">
            Go back
          </button>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const trendData = analytics.hourly_trends?.map(trend => ({
    time: new Date(trend.hour).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    uptime: trend.uptime_percentage,
    checks: trend.total_checks
  })) || [];

  const statusDistribution = [
    { name: 'Up', value: analytics.uptime_analytics.up_checks, color: '#10b981' },
    { name: 'Down', value: analytics.uptime_analytics.down_checks, color: '#ef4444' }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 mb-8 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <button 
                onClick={onBack}
                className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-4"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Dashboard
              </button>
              <h1 className="text-3xl font-bold text-slate-900">{websiteName} Analytics</h1>
              <p className="text-slate-600">Detailed performance insights and monitoring data</p>
            </div>
            <div className="flex items-center gap-4">
              <select 
                value={timeRange}
                onChange={(e) => setTimeRange(Number(e.target.value))}
                className="px-4 py-2 border border-slate-200 rounded-lg bg-white"
              >
                <option value={24}>Last 24 hours</option>
                <option value={72}>Last 3 days</option>
                <option value={168}>Last 7 days</option>
              </select>
              <button 
                onClick={fetchAnalytics}
                className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Uptime</p>
                <p className="text-3xl font-bold text-green-600">
                  {analytics.uptime_analytics.uptime_percentage}%
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Avg Response Time</p>
                <p className="text-3xl font-bold text-blue-600">
                  {analytics.response_time_analytics.avg_response_time}s
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Total Checks</p>
                <p className="text-3xl font-bold text-slate-900">
                  {analytics.uptime_analytics.total_checks}
                </p>
              </div>
              <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-slate-600" />
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Incidents</p>
                <p className="text-3xl font-bold text-red-600">
                  {analytics.uptime_analytics.down_checks}
                </p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Uptime Trend Chart */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900 mb-6">Uptime Trend</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="uptime" 
                    stroke="#10b981" 
                    strokeWidth={2}
                    dot={{ fill: '#10b981' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Status Distribution */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900 mb-6">Status Distribution</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    dataKey="value"
                    data={statusDistribution}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {statusDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-6">Recent Activity</h3>
          <div className="space-y-4 max-h-64 overflow-y-auto">
            {analytics.history?.slice(0, 10).map((record, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-b-0">
                <div className="flex items-center gap-3">
                  {record.status === 'UP' ? 
                    <CheckCircle className="w-4 h-4 text-green-500" /> : 
                    <XCircle className="w-4 h-4 text-red-500" />
                  }
                  <span className="text-sm text-slate-600">
                    Status: <span className="font-medium">{record.status}</span>
                  </span>
                  {record.response_time && (
                    <span className="text-sm text-slate-500">
                      ({record.response_time}s)
                    </span>
                  )}
                </div>
                <span className="text-sm text-slate-500">
                  {new Date(record.checked_at).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Main App Component
function App() {
  const [statusList, setStatusList] = useState([]);
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState('landing'); // landing, dashboard, analytics
  const [selectedWebsite, setSelectedWebsite] = useState('');
  const [globalStats, setGlobalStats] = useState(null);

  // Fetch all statuses
  const fetchStatuses = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/status');
      if (!response.ok) throw new Error('Failed to fetch');
      const data = await response.json();
      setStatusList(data);
    } catch (error) {
      console.error('Error fetching statuses:', error);
      setError('Failed to fetch website statuses');
    }
  };

  // Fetch global stats
  const fetchGlobalStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/stats');
      if (response.ok) {
        const data = await response.json();
        setGlobalStats(data);
      }
    } catch (error) {
      console.error('Error fetching global stats:', error);
    }
  };

  useEffect(() => {
    if (currentView === 'dashboard') {
      fetchStatuses();
      fetchGlobalStats();
      
      // Auto-refresh every 30 seconds
      const interval = setInterval(() => {
        fetchStatuses();
        fetchGlobalStats();
      }, 30000);
      
      return () => clearInterval(interval);
    }
  }, [currentView]);

  // Add status handler
  const addStatusHandler = async () => {
    if (!name.trim() || !url.trim()) {
      setError('Please fill in both name and URL fields');
      return;
    }

    try {
      new URL(url.startsWith('http') ? url : `https://${url}`);
    } catch {
      setError('Please enter a valid URL');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const finalUrl = url.startsWith('http') ? url : `https://${url}`;
      const response = await fetch('http://localhost:8000/api/status', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
          url: finalUrl,
          status: 'Checking'
        })
      });
      
      if (!response.ok) throw new Error('Failed to add website');
      
      setName('');
      setUrl('');
      await fetchStatuses();
    } catch (error) {
      console.error('Error adding status:', error);
      setError('Failed to add website. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Delete status handler
  const deleteStatusHandler = async (name) => {
    try {
      const response = await fetch(`http://localhost:8000/api/status/${name}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to delete');
      await fetchStatuses();
    } catch (error) {
      console.error('Error deleting status:', error);
      setError('Failed to delete website');
    }
  };

  // View analytics handler
  const viewAnalyticsHandler = (websiteName) => {
    setSelectedWebsite(websiteName);
    setCurrentView('analytics');
  };

  // Calculate stats
  const stats = {
    total: statusList.length,
    up: statusList.filter(s => s.status === 'UP').length,
    down: statusList.filter(s => s.status === 'Down').length
  };

  // Landing Page Component
  const LandingPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-green-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
      </div>

      <header className="relative max-w-6xl mx-auto px-6 py-16">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-50 to-green-50 text-slate-700 px-4 py-2 rounded-full text-sm font-semibold mb-6 border border-blue-100">
            <Activity className="w-4 h-4 text-blue-600" />
            Advanced Website Monitoring
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6 bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 bg-clip-text text-transparent">
            Website Status Monitor
          </h1>
          
          <p className="text-xl text-slate-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Monitor your websites with real-time analytics, instant alerts, and comprehensive 
            uptime tracking. Keep your digital presence reliable and your users happy.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <button
              onClick={() => setCurrentView('dashboard')}
              className="group bg-black text-white px-8 py-4 rounded-xl font-semibold hover:bg-gray-800 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              <span className="flex items-center gap-2">
                Start Monitoring
                <Monitor className="w-5 h-5 group-hover:scale-110 transition-transform" />
              </span>
            </button>
            <button className="bg-white text-slate-900 px-8 py-4 rounded-xl font-semibold hover:bg-slate-50 transition-all duration-200 border border-slate-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
              View Demo
            </button>
          </div>

          {/* Feature highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="bg-white/70 backdrop-blur-sm border border-white/50 rounded-2xl p-6 shadow-lg">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">99.9% Accuracy</h3>
              <p className="text-slate-600 text-sm">Reliable monitoring with minimal false positives</p>
            </div>

            <div className="bg-white/70 backdrop-blur-sm border border-white/50 rounded-2xl p-6 shadow-lg">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Rich Analytics</h3>
              <p className="text-slate-600 text-sm">Detailed insights and performance metrics</p>
            </div>

            <div className="bg-white/70 backdrop-blur-sm border border-white/50 rounded-2xl p-6 shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <Bell className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Instant Alerts</h3>
              <p className="text-slate-600 text-sm">Get notified immediately when issues occur</p>
            </div>
          </div>
        </div>
      </header>
    </div>
  );

  // Dashboard Component
  const Dashboard = () => (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
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

          {/* Global Stats */}
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
          {/* Add Website Section */}
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

          {/* Website List */}
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

  // Route based on current view
  if (currentView === 'analytics') {
    return (
      <AnalyticsDashboard 
        websiteName={selectedWebsite} 
        onBack={() => setCurrentView('dashboard')} 
      />
    );
  }

  return currentView === 'dashboard' ? <Dashboard /> : <LandingPage />;
}

export default App;