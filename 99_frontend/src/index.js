import React from 'react';
import ReactDOM from 'react-dom/client';

import Redux from './redux'
import App from './app';

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <Redux>
            <App />
        </Redux>
    </React.StrictMode>
)