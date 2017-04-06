const _sharedBaseUrl = 'https://inthe.am/api/v2/'

const subscribeHook = (z, bundle) => {
  // bundle.targetUrl has the Hook URL this app should call when a recipe is created.
  const data = {
    target_url: bundle.targetUrl,
    event: 'task.any',
  };

  // You can build requests and our client will helpfully inject all the variables
  // you need to complete. You can also register middleware to control this.
  const promise = z.request({
    url: `${_sharedBaseUrl}hooks/`,
    method: 'POST',
    body: JSON.stringify(data)
  });

  // You may return a promise or a normal data structure from any perform method.
  return promise.then((response) => JSON.parse(response.content));
};

const unsubscribeHook = (z, bundle) => {
  // bundle.subscribeData contains the parsed response JSON from the subscribe
  // request made initially.
  const hookId = bundle.subscribeData.id;

  // You can build requests and our client will helpfully inject all the variables
  // you need to complete. You can also register middleware to control this.
  const promise = z.request({
    url: `${_sharedBaseUrl}/hooks/${hookId}/`,
    method: 'DELETE',
  });

  // You may return a promise or a normal data structure from any perform method.
  return promise.then((response) => JSON.parse(response.content));
};

const getTask = (z, bundle) => {
  return [bundle.cleanedRequest];
};

const getFallbackRealTask = (z, bundle) => {
  // For the test poll, you should get some real data, to aid the setup process.
  const promise = z.request({
    url: `${_sharedBaseUrl}/tasks/`,
    params: {}
  });
  return promise.then((response) => JSON.parse(response.content));
};

// We recommend writing your triggers separate like this and rolling them
// into the App definition at the end.
module.exports = {
  key: 'task',

  // You'll want to provide some helpful display labels and descriptions
  // for users. Zapier will put them into the UX.
  noun: 'Task',
  display: {
    label: 'New or changed Task',
    description: 'Trigger when a task is created or changed.'
  },

  // `operation` is where the business logic goes.
  operation: {

    // `inputFields` can define the fields a user could provide,
    // we'll pass them in as `bundle.inputData` later.
    inputFields: [
    ],

    type: 'hook',

    performSubscribe: subscribeHook,
    performUnsubscribe: unsubscribeHook,

    perform: getTask,
    performList: getFallbackRealTask,

    sample: {
      id: 'ff1c2fc0-936d-49f3-839e-87cb8b7f350e',
      description: 'Forget bananna label image sound.',
    }
  }
};
