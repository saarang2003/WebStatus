import React, { useState, useEffect } from 'react';
import { Monitor, Globe, CheckCircle, XCircle, Clock, Plus, Trash2, Activity, Users, Zap } from 'lucide-react';

// StatusItem Component
function StatusItem({ status, onDelete }) {
  const getStatusIcon = (statusValue) => {
    switch (statusValue) {
      case 'UP':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'Down':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (statusValue) => {
    switch (statusValue) {
      case 'UP':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'Down':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Globe className="w-4 h-4 text-slate-500" />
            <h3 className="font-semibold text-slate-900">{status.name}</h3>
          </div>
          <p className="text-sm text-slate-600 mb-3 break-all">{status.url}</p>
          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border text-sm font-medium ${getStatusColor(status.status)}`}>
            {getStatusIcon(status.status)}
            {status.status}
          </div>
        </div>
        <button
          onClick={() => onDelete(status.name)}
          className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          title="Delete website"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// StatusView Component
function StatusView({ statusList, onDelete }) {
  if (!statusList || statusList.length === 0) {
    return (
      <div className="text-center py-12">
        <Monitor className="w-12 h-12 text-slate-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-slate-900 mb-2">No websites being monitored</h3>
        <p className="text-slate-600">Add a website to start monitoring its status</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {statusList.map((status, index) => (
        <StatusItem key={index} status={status} onDelete={onDelete} />
      ))}
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
  const [showDashboard, setShowDashboard] = useState(false);

  // Fetch all statuses
  const fetchStatuses = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/status');
      if (!response.ok) throw new Error('Failed to fetch');
      const data = await response.json();
      setStatusList(data);
    } catch (error) {
      console.error('Error fetching statuses:', error);
      setError('Failed to fetch website statuses');
    }
  };

  useEffect(() => {
    if (showDashboard) {
      fetchStatuses();
    }
  }, [showDashboard]);

  // Add status handler
  const addStatusHandler = async () => {
    if (!name.trim() || !url.trim()) {
      setError('Please fill in both name and URL fields');
      return;
    }

    // Basic URL validation
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
      const response = await fetch('http://localhost:8000/api/status/', {
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

  // Calculate stats
  const stats = {
    total: statusList.length,
    up: statusList.filter(s => s.status === 'UP').length,
    down: statusList.filter(s => s.status === 'Down').length
  };

  // Landing Page Component
  const LandingPage = () => (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="max-w-4xl mx-auto px-6 py-8">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-slate-100 text-slate-600 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider mb-4">
            <Activity className="w-3 h-3" />
            Real-time Monitoring
          </div>
          <h1 className="text-4xl font-bold text-slate-900 mb-4">
            Website Status Checker
          </h1>
          <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
            Monitor your websites 24/7 and get instant notifications when they go down. 
            Keep your online presence reliable and your users happy.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => setShowDashboard(true)}
              className="bg-black text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors"
            >
              Start Monitoring
            </button>
            <button className="bg-slate-100 text-slate-900 px-6 py-3 rounded-lg font-semibold hover:bg-slate-200 transition-colors border border-slate-200">
              Learn More
            </button>
          </div>
        </div>
      </header>

      {/* Trust Section */}
      <section className="max-w-4xl mx-auto px-6 py-16">
        <div className="flex flex-col md:flex-row items-center justify-center gap-8 text-center">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-slate-600" />
            <span className="text-slate-600 text-sm">Trusted by 1000+ websites</span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-slate-600" />
            <span className="text-slate-600 text-sm">99.9% uptime guaranteed</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-slate-600" />
            <span className="text-slate-600 text-sm">5-minute check intervals</span>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="max-w-4xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-3xl font-bold text-slate-900 mb-2">99.9%</div>
            <div className="text-slate-600">Uptime Accuracy</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-900 mb-2">5 min</div>
            <div className="text-slate-600">Check Frequency</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-900 mb-2">24/7</div>
            <div className="text-slate-600">Monitoring</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-4xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-slate-900 text-center mb-12">Why Choose Our Monitoring?</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
            <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center mb-4">
              <Monitor className="w-6 h-6 text-slate-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Real-time Monitoring</h3>
            <p className="text-slate-600 text-sm">Get instant alerts when your website goes down with our 5-minute check intervals.</p>
          </div>
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
            <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center mb-4">
              <Activity className="w-6 h-6 text-slate-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Detailed Analytics</h3>
            <p className="text-slate-600 text-sm">Track your website's uptime history and performance over time with detailed reports.</p>
          </div>
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
            <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center mb-4">
              <Globe className="w-6 h-6 text-slate-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Global Monitoring</h3>
            <p className="text-slate-600 text-sm">Monitor your websites from multiple locations worldwide for accurate results.</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="max-w-4xl mx-auto px-6 py-16 border-t border-slate-200">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h4 className="font-semibold text-slate-900 mb-4">Product</h4>
            <div className="space-y-2 text-sm text-slate-600">
              <div>Features</div>
              <div>Pricing</div>
              <div>API</div>
            </div>
          </div>
          <div>
            <h4 className="font-semibold text-slate-900 mb-4">Company</h4>
            <div className="space-y-2 text-sm text-slate-600">
              <div>About</div>
              <div>Blog</div>
              <div>Careers</div>
            </div>
          </div>
          <div>
            <h4 className="font-semibold text-slate-900 mb-4">Resources</h4>
            <div className="space-y-2 text-sm text-slate-600">
              <div>Documentation</div>
              <div>Help Center</div>
              <div>Status</div>
            </div>
          </div>
          <div>
            <h4 className="font-semibold text-slate-900 mb-4">Legal</h4>
            <div className="space-y-2 text-sm text-slate-600">
              <div>Privacy</div>
              <div>Terms</div>
              <div>Security</div>
            </div>
          </div>
        </div>
        <div className="border-t border-slate-200 mt-8 pt-8 text-center text-sm text-slate-600">
          © {new Date().getFullYear()} Website Status Checker. All rights reserved.
        </div>
      </footer>
    </div>
  );

  // Dashboard Component
  const Dashboard = () => (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="bg-white border border-slate-200 rounded-lg p-6 mb-8 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Website Status Dashboard</h1>
              <p className="text-slate-600">Monitor your websites in real-time</p>
            </div>
            <button
              onClick={() => setShowDashboard(false)}
              className="text-slate-600 hover:text-slate-900 text-sm font-medium"
            >
              ← Back to Home
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-slate-900">{stats.total}</div>
              <div className="text-sm text-slate-600">Total Websites</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.up}</div>
              <div className="text-sm text-slate-600">Online</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{stats.down}</div>
              <div className="text-sm text-slate-600">Offline</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Add Website Section */}
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-6">
              <Plus className="w-5 h-5 text-slate-600" />
              <h2 className="text-lg font-semibold text-slate-900">Add Website</h2>
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
                  placeholder="e.g., https://example.com"
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
              <p className="text-xs text-slate-600">
                * Website status is checked automatically every 5 minutes
              </p>
            </div>
          </div>

          {/* Status List Section */}
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-6">
              <Monitor className="w-5 h-5 text-slate-600" />
              <h2 className="text-lg font-semibold text-slate-900">Monitoring Websites</h2>
            </div>
            <StatusView statusList={statusList} onDelete={deleteStatusHandler} />
          </div>
        </div>
      </div>
    </div>
  );

  return showDashboard ? <Dashboard /> : <LandingPage />;
}

export default App;