import React from 'react';
import { Route, IndexRoute } from 'react-router';

import App from './components/app';
import LandingPage from './components/LandingPage';
import Features from './components/Features';

export default(
  <Route path="/" component={App}>
    <IndexRoute component={LandingPage} />
    <Route component={Features} path='features' />
  </Route>
);
