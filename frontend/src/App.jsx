import React, { useState, useEffect } from 'react';
import StatusView from './components/StatusViewList';
import axios from 'axios';

function App() {
  const [statusList, setStatusList] = useState([{}]);
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const status = 'Checking';

  // Read all statuses
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/status')
      .then(res => {
        setStatusList(res.data);
      });
  }, []);

  // Add status
  const addStatusHandler = () => {
    axios.post('http://localhost:8000/api/status/', { name, url, status })
      .then(res => console.log(res));
    window.location.reload(false);
  };

  return (
    <div className="w-[95%] mx-auto bg-white mt-4 p-4 shadow-lg">
      <h1 className="text-white bg-blue-600 text-xl font-bold px-4 py-2 rounded-t">Website Status Checker</h1>
      <h6 className="text-white bg-blue-500 px-4 py-2 mb-4 rounded-b">FASTAPI - React - MongoDB</h6>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Add Website Section */}
        <div className="bg-gray-100 p-4 rounded shadow">
          <h5 className="text-white bg-gray-800 px-4 py-2 rounded text-lg mb-3">Add Website</h5>
          <div className="space-y-3">
            <input
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
              onChange={e => setName(e.target.value)}
              placeholder="Name"
            />
            <input
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
              onChange={e => setUrl(e.target.value)}
              placeholder="URL"
            />
            <button
              onClick={addStatusHandler}
              className="bg-blue-600 text-white font-semibold px-6 py-2 rounded-full hover:bg-blue-700"
            >
              Add Website
            </button>
            <p className="text-red-600 text-sm">
              *Status of websites is checked every 5 minutes automatically
            </p>
            <img
              src="https://infini7y.tk/wp-content/uploads/2022/11/temp.png"
              alt="temp"
              className="w-full rounded"
            />
          </div>
        </div>

        {/* Status List Section */}
        <div className="bg-gray-100 p-4 rounded shadow">
          <h5 className="text-white bg-gray-800 px-4 py-2 rounded text-lg mb-3">Monitoring Websites</h5>
          <StatusView StatusList={statusList} />
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center text-sm text-black bg-yellow-400 py-2 mt-6 fixed bottom-0 left-0 w-full">
        Copyright &copy; {new Date().getFullYear()} To Niraj-Dilshan, All rights reserved
      </footer>
    </div>
  );
}

export default App;
