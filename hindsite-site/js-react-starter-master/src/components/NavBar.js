import React, { Component } from 'react';
import {Router, Route, Link, RouteHandler} from 'react-router';


// example class based component (smart component)
class NavBar extends Component {
  constructor(props) {
    super(props);

    // init component state here
    this.state = {};
  }

  render() {
    return (
      <div id="nav-bar-container">
        <div className="row" id="nav-bar-row">
          <div className="col-sm-4 col-sm-offset-1">
            <img id="nav-bar-logo" src='src/static/img/logo-light.png'/>
             hindsite
          </div>
          <div id="nav-bar-options" className="col-sm-5 col-sm-offset-2">
            <div className="col-sm-3">
              <Link className="redirect-link" to="/features" >
                Features
              </Link>
            </div>
            <div className="col-sm-5" id="use-cases-div">
              <Link className="redirect-link" to="/features" >
                Use Cases
              </Link>
            </div>
            <div className="col-sm-4">
              <Link className="redirect-link" to="/features" >
                About
              </Link>
            </div>
          </div>

        </div>
      </div>

    );
  }
}

export default NavBar;


// <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
//   <div class="container">
//     <div class="navbar-header">
//       <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
//         <span class="sr-only">Toggle navigation</span>
//         <span class="icon-bar"></span>
//         <span class="icon-bar"></span>
//         <span class="icon-bar"></span>
//       </button>
//       <a class="navbar-brand" href="#">hindsite</a>
//     </div>
//     <!-- <div id="navbar" class="navbar-collapse collapse">
//       <form class="navbar-form navbar-right" role="form">
//         <div class="form-group">
//           <input type="text" placeholder="Email" class="form-control">
//         </div>
//         <div class="form-group">
//           <input type="password" placeholder="Password" class="form-control">
//         </div>
//         <button type="submit" class="btn btn-success">Sign in</button>
//       </form>
//     </div><!--/.navbar-collapse --> -->
//   </div>
// </nav>
