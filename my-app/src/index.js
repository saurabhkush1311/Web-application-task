// index.js
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';  // Make sure the import path is correct
import './index.css';  // Import any global styles if needed

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
