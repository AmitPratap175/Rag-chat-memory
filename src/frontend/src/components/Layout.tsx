import React from 'react';
import { NavLink } from 'react-router-dom';
import '../App.css';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="bw-root">
      {/* Sidebar */}
      <aside className="bw-sidebar">
        <div className="sidebar-header">
          <img src="/normal_portrait.svg" alt="Brahmware logo" className="sidebar-logo" />
        </div>
        <nav className="sidebar-nav">
          <ul>
            <li><NavLink to="/" end>Dashboard</NavLink></li>
            <li><NavLink to="/add-url">Add URL</NavLink></li>
            <li><NavLink to="/crawls">Crawl Management</NavLink></li>
            <li><NavLink to="/questions">Question Bank</NavLink></li>
            <li><NavLink to="/quiz">Quiz Player</NavLink></li>
            <li><NavLink to="/chat">Chat</NavLink></li>
          </ul>
        </nav>
        <div className="sidebar-bottom">
          <button className="sidebar-pricing-btn">Pricing</button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="bw-chat-bg">
        {children}
      </main>
    </div>
  );
};

export default Layout;
