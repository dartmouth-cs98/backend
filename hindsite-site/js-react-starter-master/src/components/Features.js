import React, { Component } from 'react';
import NavBar from './NavBar.js';

// example class based component (smart component)
class Features extends Component {
  constructor(props) {
    super(props);

    // init component state here
    this.state = {};
  }

  render() {
    return (
      <div>
        <NavBar/>
        GREAT!
      </div>
    );
  }
}

export default Features;
