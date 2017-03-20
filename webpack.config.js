var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

const ExtractTextPlugin = require('extract-text-webpack-plugin');

const autoprefixer = require('autoprefixer');

module.exports = {
  stats: { colors: true },
  devtool: 'inline-source-map',
  devServer: { inline: true },
  entry: ['babel-polyfill', './hindsite/static/src'],
  output: {
    path: './hindsite/static/src/bundles',
    filename: "bundle.js",
  },
  module: {
    loaders: [{
      test: /\.js$/,
      exclude: /node_modules/,
      loader: 'babel',
    },
    {
      test: /\.scss/,
      loader: ExtractTextPlugin.extract('style-loader', 'css-loader!sass-loader!postcss-loader'),
    },
    {
      test: /\.css/,
      loader: "style-loader!css-loader",
    },
      // You could also use other loaders the same way. I. e. the autoprefixer-loader
    ],
  },
  postcss: [autoprefixer({ browsers: ['last 2 versions'] })],
  plugins: [
    new ExtractTextPlugin('bundle.css'),
    new BundleTracker({filename: './webpack-stats.json'}),
  ],
};
