import React, { Component } from 'react';
import NavBar from './NavBar.js';
import {Router, Route, Link, RouteHandler} from 'react-router';

// example class based component (smart component)
class LandingPage extends Component {
  constructor(props) {
    super(props);
    // init component state here
    this.state = {};
  }

  installApp(){
    console.log("here");
    chrome.webstore.install();
  }
  render() {
    // <div id="nav-bar-jumbotron">

    // <img src='src/static/img/blurry-landing.png' id="landing-page-bck-img"/>
    return (
      <div id="landing-page-container">
        <NavBar />
        <div className="jumbotron">


          <div className="container">
            <h1>hindsite</h1>
            <p>history that’s finally 20/20</p>
            <div className="wrapper">
            <button className="btn btn-primary btn-lg"
                onClick={chrome.webstore.install}
                role="button">
                  <i className="fa fa-plus"></i> Add to Chrome
            </button>
            </div>
          </div>
        </div>

        <div className="container">
          <div className="row">
            <div className="col-md-4">
              <h2 id="features">Lookback</h2>
              <p>This feature allows you to see your history in an intuitive timeline view. It shows you when pages were opened, closed, active, where they overlap and how you moved from one page to another.</p>
            </div>
            <div className="col-md-4">
              <h2 id="features">Categories</h2>
              <p>By using hindsites categorization tool, you are able to easily tag pages to go back to later. When you are ready, you can go to your categories page to see all of the pages you have categorized.</p>
            </div>
            <div className="col-md-4">
              <h2 id="features">Search</h2>
              <p>Unlike Chrome History, hindsite searches pages in your history by page content as well as by title. This means that hindsite will find your search terms anywhere they are mentioned in the pages you visited.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }
}


export default LandingPage;
