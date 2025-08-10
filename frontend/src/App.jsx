import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import LandingPage from './components/LandingPage';
import AnalyticsDashboard from './components/AnalyticsDashboard';

function App() {
  const [statusList, setStatusList] = useState([]);
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState('landing');
  const [selectedWebsite, setSelectedWebsite] = useState('');
  const [globalStats, setGlobalStats] = useState(null);

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
      const interval = setInterval(() => {
        fetchStatuses();
        fetchGlobalStats();
      }, 30000);
      return () => clearInterval(interval);
    }
  }, [currentView]);

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

  const viewAnalyticsHandler = (websiteName) => {
    setSelectedWebsite(websiteName);
    setCurrentView('analytics');
  };

  const stats = {
    total: statusList.length,
    up: statusList.filter(s => s.status === 'UP').length,
    down: statusList.filter(s => s.status === 'Down').length
  };

  if (currentView === 'analytics') {
    return (
      <AnalyticsDashboard 
        websiteName={selectedWebsite} 
        onBack={() => setCurrentView('dashboard')} 
      />
    );
  }

  return currentView === 'dashboard' ? (
    <Dashboard 
      stats={stats}
      globalStats={globalStats}
      statusList={statusList}
      name={name}
      url={url}
      setName={setName}
      setUrl={setUrl}
      error={error}
      isLoading={isLoading}
      addStatusHandler={addStatusHandler}
      deleteStatusHandler={deleteStatusHandler}
      viewAnalyticsHandler={viewAnalyticsHandler}
      fetchStatuses={fetchStatuses}
      setCurrentView={setCurrentView}
    />
  ) : (
    <LandingPage setCurrentView={setCurrentView} />
  );
}

export default App;