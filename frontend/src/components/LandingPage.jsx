import React from 'react';
import { Activity, CheckCircle, BarChart3, Bell, Monitor } from 'lucide-react';

function LandingPage({ setCurrentView }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
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
}

export default LandingPage;