import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// This code finds the 'root' div in our HTML file and tells React to render our main 'App' component inside it.
ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);