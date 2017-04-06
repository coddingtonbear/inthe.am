const TaskResource = require('./resources/task');
const TaskTrigger = require('./triggers/task');

const authentication = {
  type: 'custom',
  test: {
    'url': 'https://inthe.am/api/v2/user/status/'
  },
  fields: [
    {key: 'api_key', type: 'string', required: true, helpText: 'Found on your settings page.'}
  ]
}

const addApiKeyToHeader = (request, z, bundle) => {
  request.headers.Authorization = `Token ${bundle.authData.api_key}`;
  return request;
};

// We can roll up all our behaviors in an App.
const App = {
  // This is just shorthand to reference the installed dependencies you have. Zapier will
  // need to know these before we can upload
  version: require('./package.json').version,
  platformVersion: require('zapier-platform-core').version,

  authentication: authentication,
  // beforeRequest & afterResponse are optional hooks into the provided HTTP client
  beforeRequest: [
    addApiKeyToHeader,
  ],

  afterResponse: [
  ],

  // If you want to define optional resources to simplify creation of triggers, searches, creates - do that here!
  resources: {
    [TaskResource.key]: TaskResource,
  },

  // If you want your trigger to show up, you better include it here!
  triggers: {
    [TaskTrigger.key]: TaskTrigger,
  },

  // If you want your searches to show up, you better include it here!
  searches: {
  },

  // If you want your creates to show up, you better include it here!
  creates: {
  }
};

// Finally, export the app.
module.exports = App;
