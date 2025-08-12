import React from 'react';
import { NavLink } from 'react-router-dom';

const NavigationBar: React.FC = () => {
    return (
        <nav className="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
            <div className="container-fluid">
                <NavLink className="navbar-brand" to="/">
                    CAT Question Bank
                </NavLink>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarNav">
                    <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                        <li className="nav-item">
                            <NavLink className="nav-link" to="/varc">VARC</NavLink>
                        </li>
                        <li className="nav-item">
                            <NavLink className="nav-link" to="/quant">Quant</NavLink>
                        </li>
                        <li className="nav-item">
                            <NavLink className="nav-link" to="/dilr">DILR</NavLink>
                        </li>
                        <li className="nav-item">
                            <NavLink className="nav-link" to="/add-url">Add URL</NavLink>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    );
};

export default NavigationBar;
