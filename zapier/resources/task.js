const _sharedBaseUrl = 'https://inthe.am/api/v2/'


// get a single task
const getTask = (z, bundle) => {
  const responsePromise = z.request({
    url: `${_sharedBaseUrl}tasks/${bundle.inputData.id}/`,
  });
  return responsePromise
    .then(response => JSON.parse(response.content));
};

// get a list of tasks
const listTasks = (z) => {
  const responsePromise = z.request({
    url: `${_sharedBaseUrl}tasks/`,
    params: {
      order_by: 'id desc'
    }
  });
  return responsePromise
    .then(response => JSON.parse(response.content));
};

// find a particular task by name
const searchTasks = (z, bundle) => {
  const responsePromise = z.request({
    url: `${_sharedBaseUrl}tasks/`,
    params: {
      query: `name:${bundle.inputData.name}`
    }
  });
  return responsePromise
    .then(response => JSON.parse(response.content));
};

// create a task
const createTask = (z, bundle) => {
  const responsePromise = z.request({
    method: 'POST',
    url: `${_sharedBaseUrl}tasks/`,
    body: {
      name: bundle.inputData.name // json by default
    }
  });
  return responsePromise
    .then(response => JSON.parse(response.content));
};

module.exports = {
  key: 'task',
  noun: 'Task',
  get: {
    display: {
      label: 'Get Task',
      description: 'Gets a task from Inthe.AM.'
    },
    operation: {
      inputFields: [
        {key: 'id', required: true}
      ],
      perform: getTask
    }
  },
  /*
  list: {
    display: {
      label: 'New Task',
      description: 'Lists the tasks on Inthe.AM.'
    },
    operation: {
      perform: listTasks
    }
  },
  search: {
    display: {
      label: 'Find Task',
      description: 'Finds a task by searching on inthe.AM.'
    },
    operation: {
      inputFields: [
        {key: 'description', required: true}
      ],
      perform: searchTasks
    },
  },*/
  create: {
    display: {
      label: 'Create Task',
      description: 'Creates a new task on Inthe.AM.'
    },
    operation: {
      inputFields: [
        {key: 'description', required: true, label: 'Description of task'},
        {key: 'due', required: false, label: 'Due date for task', type: 'datetime'},
      ],
      perform: createTask
    },
  },
  sample: {
    id: 'ff1c2fc0-936d-49f3-839e-87cb8b7f350e',
    description: 'Plant unicorn farm in back yard.',
  }
};
