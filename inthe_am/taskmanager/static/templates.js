this["Ember"] = this["Ember"] || {};
this["Ember"]["TEMPLATES"] = this["Ember"]["TEMPLATES"] || {};

this["Ember"]["TEMPLATES"]["about"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  


  data.buffer.push("<div class=\"row standalone\">\n    <h1>Inthe.AM</h1>\n    <p>\n        Access, create, and modify your taskwarrior tasks from a\n        web browser, anywhere.\n    </p>\n</div>\n");
  
});

this["Ember"]["TEMPLATES"]["api_access"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', hashTypes, hashContexts, escapeExpression=this.escapeExpression;


  data.buffer.push("<div class=\"row standalone\">\n    <h2>Accessing your tasks via the REST API</h2>\n\n    <p>\n        Your Taskwarrior tasks are accessible via a REST API; you can\n        use this to programatically query, create, complete, or change\n        tasks in your task list.\n    </p>\n\n\n    <h3>Authentication</h3>\n\n    <table class=\"pure-table pure-table-horizontal\">\n        <tr>\n            <th>\n                Username\n            </th>\n            <td>\n                ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "controllers.application.user.username", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n            </td>\n        </tr>\n        <tr>\n            <th>\n                Api Key\n            </th>\n            <td>\n                ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "controllers.application.user.api_key", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n            </td>\n        </tr>\n    </table>\n\n    <p>\n        Using your API key and username, use the header \"<code>Authorization</code>\";\n        for an example:\n    </p>\n\n    <code>\n    <pre>\n        Authorization: ApiKey ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "controllers.application.user.username", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(":");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "controllers.application.user.api_key", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n    </pre>\n    </code>\n\n    <h3>Endpoints</h3>\n\n    <h4>Pending Tasks</h4>\n\n    <table class=\"pure-table pure-table-horizontal\">\n        <tr>\n            <th>\n                Task List\n            </th>\n            <td>\n                <code>https://inthe.am/api/v1/task/</code>\n            </td>\n        </tr>\n        <tr>\n            <th>\n                Task Detail\n            </th>\n            <td>\n                <code>https://inthe.am/api/v1/task/<b>&lt;TASK UUID&gt;</b>/</code>\n            </td>\n        </tr>\n    </table>\n\n\n    <table class=\"pure-table pure-table-horizontal\">\n        <thead>\n            <tr>\n                <th>Method</th>\n                <th>Description</th>\n            </tr>\n        </thead>\n        <tbody>\n            <tr>\n                <td>GET</td>\n                <td>Retrieve an existing task.</td>\n            </tr>\n            <tr>\n                <td>POST</td>\n                <td>\n                    Create a new task.<br />\n                    <em>This is used with only the 'Task List' endpoint</em>.\n                </td>\n            </tr>\n            <tr>\n                <td>PUT</td>\n                <td>\n                    Update an existing task.<br />\n                    <em>This is used with only the 'Task Detail' endpoint</em>.\n                </td>\n            </tr>\n            <tr>\n                <td>DELETE</td>\n                <td>\n                    Marks an existing task as completed.\n                    After ran, the task will only be listed from 'Completed Task' endpoints.<br />\n                    <em>This is used with only the 'Task Detail' endpoint</em>.\n                </td>\n            </tr>\n        </tbody>\n    </table>\n\n    <h5>Special Task Actions</h5>\n\n    <table>\n        <thead>\n            <th>URL</th>\n            <th>Method</th>\n            <th>Description</th>\n        </thead>\n        <tbody>\n            <tr>\n                <td><code>https://inthe.am/api/v1/task/<b>&lt;TASK UUID&gt;</b>/delete/</code></td>\n                <td>POST</td>\n                <td>\n                    Marks an existing task as deleted.\n                    After ran, this task will not be listed from any endpoint.\n                </td>\n            </tr>\n            <tr>\n                <td><code>https://inthe.am/api/v1/task/<b>&lt;TASK UUID&gt;</b>/start/</code></td>\n                <td>POST</td>\n                <td>\n                    Marks an existing task as started.\n                </td>\n            </tr>\n            <tr>\n                <td><code>https://inthe.am/api/v1/task/<b>&lt;TASK UUID&gt;</b>/stop/</code></td>\n                <td>POST</td>\n                <td>\n                    Marks an existing task as stopped.\n                </td>\n            </tr>\n            <tr>\n                <td><code>https://inthe.am/api/v1/task/lock/</code></td>\n                <td>DELETE</td>\n                <td>\n                    Force-unlocks the task list.  This is a dangerous operation\n                    and could render your tasks inaccessible.\n                    <br /><br />\n                    Only a single task operation is allowed to occur on a\n                    user's repository at a time, and in order to prevent\n                    simultaneous actions a lock is used.  In very rare\n                    situations, problems may occur that cause a lock\n                    to not be released following an action.  Please be careful.\n                    <br />\n                    <ul>\n                        <li><b>200</b>: Unlocked successfully.</li>\n                        <li><b>404</b>: The task list is not currently locked.</li>\n                    <ul>\n                </td>\n            </tr>\n            <tr>\n                <td><code>https://inthe.am/api/v1/task/lock/</code></td>\n                <td>GET</td>\n                <td>\n                    Returns whether or not the task list is currently locked.\n                    <br />\n                    <ul>\n                        <li><b>200</b>: The task list is currently locked.</li>\n                        <li><b>404</b>: The task list is not currently locked.</li>\n                    <ul>\n                </td>\n            </tr>\n        </tbody>\n    </table>\n\n    <h4>Completed Tasks</h4>\n\n    <table class=\"pure-table pure-table-horizontal\">\n        <tr>\n            <th>\n                Completed Task List\n            </th>\n            <td>\n                <code>https://inthe.am/api/v1/completedtask/</code>\n            </td>\n        </tr>\n        <tr>\n            <th>\n                Completed Task Detail\n            </th>\n            <td>\n                <code>https://inthe.am/api/v1/completedtask/<b>&lt;TASK UUID&gt;</b>/</code>\n            </td>\n        </tr>\n    </table>\n\n    <table class=\"pure-table pure-table-horizontal\">\n        <thead>\n            <tr>\n                <th>Method</th>\n                <th>Description</th>\n            </tr>\n        </thead>\n        <tbody>\n            <tr>\n                <td>GET</td>\n                <td>Retrieve a completed task.</td>\n            </tr>\n        </tbody>\n    </table>\n\n    <h3>Task Format</h3>\n\n    <p>\n        Each task has the following fields:\n    </p>\n    <table class=\"pure-table pure-table-horizontal\">\n        <thead>\n            <tr>\n                <th>Field</th>\n                <th>Description</th>\n            </tr>\n        </thead>\n        <tbody>\n            <tr>\n                <td><code>id</code></td>\n                <td>\n                    The short ID number of a task.\n                    These are not stable and are generally used when\n                    using the Taskwarrior command-line client for ease-of\n                    entry; if a task is completed, all\n                    tasks may receive a new ID number.\n                </td>\n            </tr>\n            <tr>\n                <td><code>uuid</code></td>\n                <td>\n                    The unique ID number of a task.\n                    These are stable and can be used in situations where\n                    you may want to retrieve a task after it has been completed.\n                    <br />\n                    <strong>\n                        This is the primary key of the task and is a\n                        read-only property.\n                    </strong>.\n                </td>\n            </tr>\n            <tr>\n                <td><code>resource_uri</code></td>\n                <td>\n                    This is the URL at which this task can be retrieved\n                    again in the future.  It will match the URL you used\n                    for fetching this task unless you fetched this task\n                    from a listing endpoint.\n                    <strong>\n                        This is a read-only property.\n                    </strong>\n                </td>\n            </tr>\n            <tr>\n                <td><code>status</code></td>\n                <td>\n                    One of <code>pending</code>, <code>completed</code>,\n                    <code>waiting</code>, or <code>deleted</code>.\n                    New tasks default to <code>pending</code>.\n                </td>\n            </tr>\n            <tr>\n                <td><code>urgency</code></td>\n                <td>\n                    A float representing the current calculated urgency level\n                    of a task.  This is generated internally by taskwarrior\n                    and thus is a <strong>read-only property</strong>.\n                </td>\n            </tr>\n            <tr>\n                <td><code>description</code></td>\n                <td>\n                    The title of this task.\n                    <strong>This property is required.</strong>\n                </td>\n            </tr>\n            <tr>\n                <td><code>priority</code></td>\n                <td>\n                    One of <code>H</code>,\n                    <code>M</code>, or <code>L</code>.\n                </td>\n            </tr>\n            <tr>\n                <td><code>due</code></td>\n                <td>\n                    A date string representing this task's due date and time.\n                </td>\n            </tr>\n            <tr>\n                <td><code>entry</code></td>\n                <td>\n                    A date string representing this task's entry date and time.\n                </td>\n            </tr>\n            <tr>\n                <td><code>modified</code></td>\n                <td>\n                    A date string representing this task's modified date and time.\n                </td>\n            </tr>\n            <tr>\n                <td><code>start</code></td>\n                <td>\n                    A date string representing the date and time this task was started.\n                </td>\n            </tr>\n            <tr>\n                <td><code>wait</code></td>\n                <td>\n                    A date string representing the date and time to wait\n                    before listing this task in the pending task list.\n                </td>\n            </tr>\n            <tr>\n                <td><code>scheduled</code></td>\n                <td>\n                    A date string representing the date and time at which\n                    work on this task is scheduled.\n                </td>\n            </tr>\n            <tr>\n                <td><code>depends</code></td>\n                <td>\n                    A comma-separated list of task UUIDs upon which\n                    this task depends.\n                </td>\n            </tr>\n            <tr>\n                <td><code>annotations</code></td>\n                <td>\n                    A list of annotations added to this task.\n\n                    <em>\n                        Note: this is returned from Taskwarrior as a dictionary\n                        having keys <code>entry</code> (the time at which this\n                        annotation was added) and <code>description</code> (the\n                        annotation text itself), but you are also able update or\n                        create task entries by supplying simply a list of string\n                        annotations you would like your updated or created task\n                        to have.\n                    </em>\n                </td>\n            </tr>\n            <tr>\n                <td><code>tags</code></td>\n                <td>\n                    A list of tags assigned to this task.\n                </td>\n            </tr>\n            <tr>\n                <td><code>imask</code></td>\n                <td>\n                    An integer representing this task's <code>imask</code>.  This\n                    is a <strong>read-only property</strong> used internally\n                    by Taskwarrior for recurring tasks.\n                </td>\n            </tr>\n        </tbody>\n    </table>\n\n    <p>\n        Example JSON formatted task:\n    </p>\n\n    <code>\n    <pre>\n        {\n            \"annotations\": [\n                {\"description\": \"Chapter 1\", \"entry\": \"Mon, 3 Feb 2014 01:52:51 +0000\"},\n                {\"description\": \"Chapter 2\", \"entry\": \"Mon, 3 Feb 2014 01:52:53 +0000\"}\n            ],\n            \"depends\": null,\n            \"description\": \"The wheels on the bus go round and round\",\n            \"due\": null,\n            \"entry\": \"Mon, 3 Feb 2014 01:52:51 +0000\",\n            \"id\": 1,\n            \"imask\": null,\n            \"modified\": \"Mon, 3 Feb 2014 01:52:52 +0000\",\n            \"priority\": null,\n            \"project\": \"Alphaville\",\n            \"resource_uri\": \"/api/v1/task/b8d05cfe-8464-44ef-9d99-eb3e7809d337/\",\n            \"scheduled\": null,\n            \"start\": null,\n            \"status\": \"waiting\",\n            \"tags\": [\"very_unimportant\", \"delayed\"],\n            \"urgency\": -0.1,\n            \"uuid\": \"b8d05cfe-8464-44ef-9d99-eb3e7809d337\",\n            \"wait\": \"Thu, 6 Feb 2014 01:52:51 +0000\"\n        }\n    </pre>\n    </code>\n\n    <p>\n        <em>\n            Note that although the displayed task's datetime fields are\n            encoded using RFC 2822 date strings in UTC,\n            your supplied date strings will be parsed using\n            <a href=\"http://labix.org/python-dateutil#head-c0e81a473b647dfa787dc11e8c69557ec2c3ecd2\">dateutil's parse method</a>,\n            so you can provide date strings in whatever format is most convenient for you,\n            but ISO 8601 or RFC 2822 formatted dates are strongly recommended.\n            <strong>\n                Be sure to specify a time zone or offset in your date string.\n            </strong>\n        </em>\n    </p>\n    \n</div>\n");
  return buffer;
  
});

this["Ember"]["TEMPLATES"]["application"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', stack1, hashTypes, hashContexts, options, self=this, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;

function program1(depth0,data) {
  
  var buffer = '', stack1, stack2, hashTypes, hashContexts, options;
  data.buffer.push("\n        <section class=\"top-bar-section\">\n            <!-- Right Nav Section -->\n            <ul class=\"right\">\n                <li class=\"desktop-only\">\n                    ");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},inverse:self.noop,fn:self.program(2, program2, data),contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  stack2 = ((stack1 = helpers['link-to'] || depth0['link-to']),stack1 ? stack1.call(depth0, "synchronization", options) : helperMissing.call(depth0, "link-to", "synchronization", options));
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n                </li>\n                <li class=\"desktop-only\">\n                    ");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},inverse:self.noop,fn:self.program(4, program4, data),contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  stack2 = ((stack1 = helpers['link-to'] || depth0['link-to']),stack1 ? stack1.call(depth0, "sms", options) : helperMissing.call(depth0, "link-to", "sms", options));
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n                </li>\n                <li class=\"desktop-only\">\n                    ");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},inverse:self.noop,fn:self.program(6, program6, data),contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  stack2 = ((stack1 = helpers['link-to'] || depth0['link-to']),stack1 ? stack1.call(depth0, "api_access", options) : helperMissing.call(depth0, "link-to", "api_access", options));
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n                </li>\n                <li>\n                    ");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},inverse:self.noop,fn:self.program(8, program8, data),contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  stack2 = ((stack1 = helpers['link-to'] || depth0['link-to']),stack1 ? stack1.call(depth0, "configure", options) : helperMissing.call(depth0, "link-to", "configure", options));
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n                </li>\n                <li>\n                    <a href=\"/logout/\"><i class=\"fa fa-sign-out\">Log Out</i></a>\n                </li>\n            </ul>\n\n            <!-- Left Nav Section -->\n            <ul class=\"left\">\n                <li class=\"mobile-only\">\n                    ");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},inverse:self.noop,fn:self.program(10, program10, data),contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  stack2 = ((stack1 = helpers['link-to'] || depth0['link-to']),stack1 ? stack1.call(depth0, "mobileTasks", options) : helperMissing.call(depth0, "link-to", "mobileTasks", options));
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n                </li>\n                <li>\n                    <a href=\"#\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "create_task", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("><i class=\"fa fa-pencil-square-o\"></i></a>\n                </li>\n                <li>\n                    <a href=\"#\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "refresh", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("><i class=\"fa fa-refresh\"></i></a>\n                </li>\n                <li>\n                    ");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},inverse:self.noop,fn:self.program(12, program12, data),contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  stack2 = ((stack1 = helpers['link-to'] || depth0['link-to']),stack1 ? stack1.call(depth0, "tasks", options) : helperMissing.call(depth0, "link-to", "tasks", options));
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n                </li>\n            </ul>\n        </section>\n    ");
  return buffer;
  }
function program2(depth0,data) {
  
  
  data.buffer.push("<i class=\"fa fa-cloud-upload\">Sync</i>");
  }

function program4(depth0,data) {
  
  
  data.buffer.push("<i class=\"fa fa-phone\">SMS</i>");
  }

function program6(depth0,data) {
  
  
  data.buffer.push("<i class=\"fa fa-gears\">API</i>");
  }

function program8(depth0,data) {
  
  
  data.buffer.push("<i class=\"fa fa-wrench\">Settings</i>");
  }

function program10(depth0,data) {
  
  
  data.buffer.push("<i class=\"fa fa-list-ul\">Tasks</i>");
  }

function program12(depth0,data) {
  
  
  data.buffer.push("Pending");
  }

function program14(depth0,data) {
  
  
  data.buffer.push("\n        <section class=\"top-bar-section\">\n            <ul class=\"left\">\n                <li>\n                    <a href=\"/login/google-oauth2/\"><i class=\"fa fa-sign-in\">Log In with Google</i></a>\n                </li>\n            </ul>\n        </section>\n    ");
  }

  data.buffer.push("<nav class=\"top-bar\" data-topbar>\n    <ul class=\"title-area\">\n        <li class=\"name\">\n            <h1><a href=\"/\">Inthe.AM</a></h1>\n        </li>\n    </ul>\n\n    ");
  hashTypes = {};
  hashContexts = {};
  stack1 = helpers['if'].call(depth0, "controller.user.name", {hash:{},inverse:self.program(14, program14, data),fn:self.program(1, program1, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack1 || stack1 === 0) { data.buffer.push(stack1); }
  data.buffer.push("\n</nav>\n");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "outlet", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.outlet || depth0.outlet),stack1 ? stack1.call(depth0, "modal", options) : helperMissing.call(depth0, "outlet", "modal", options))));
  data.buffer.push("\n");
  return buffer;
  
});

this["Ember"]["TEMPLATES"]["configure"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', stack1, hashContexts, hashTypes, options, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;


  data.buffer.push("<div class=\"row standalone\">\n    <h2>Settings</h2>\n    <div id=\"settings_alerts\">\n    </div>\n\n    <dl class=\"accordion\" data-accordion>\n        <dd>\n            <a href=\"#custom_taskd\">Taskd Server Synchronization</a>\n            <div id=\"custom_taskd\" class=\"content active\">\n                <div class=\"row\">\n                    <div class=\"large-12 columns\">\n                        <label>Taskd Server</label>\n                        ");
  hashContexts = {'type': depth0,'id': depth0,'name': depth0,'value': depth0};
  hashTypes = {'type': "STRING",'id': "STRING",'name': "STRING",'value': "ID"};
  options = {hash:{
    'type': ("text"),
    'id': ("id_server"),
    'name': ("server"),
    'value': ("controllers.application.user.taskd_server")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.input || depth0.input),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "input", options))));
  data.buffer.push("\n                    </div>\n                    <div class=\"large-12 columns\">\n                        <label>Taskd Credentials</label>\n                        ");
  hashContexts = {'type': depth0,'id': depth0,'name': depth0,'value': depth0};
  hashTypes = {'type': "STRING",'id': "STRING",'name': "STRING",'value': "ID"};
  options = {hash:{
    'type': ("text"),
    'id': ("id_credentials"),
    'name': ("credentials"),
    'value': ("controllers.application.user.taskd_credentials")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.input || depth0.input),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "input", options))));
  data.buffer.push("\n                    </div>\n                    <div class=\"large-12 columns\">\n                        <label>Certificate</label>\n                        <input type=\"file\" name=\"certificate\" id=\"id_certificate\">\n                        <p class=\"input-note\">\n                            ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "controllers.application.user.taskd_files.taskd_certificate", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n                        </p>\n                    </div>\n                    <div class=\"large-12 columns\">\n                        <label>Key</label>\n                        <input type=\"file\" name=\"key\" id=\"id_key\">\n                        <p class=\"input-note\">\n                            ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "controllers.application.user.taskd_files.taskd_key", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n                        </p>\n                    </div>\n                    <div class=\"large-12 columns\">\n                        <label>CA Certificate</label>\n                        <p class=\"input-note\">\n                            If you select to trust the taskd server, you need not upload a CA Certificate,\n                            but uploading a certificate and requesting that we validate the taskd server\n                            using that certificate is safer.\n                        </p>\n                        ");
  hashContexts = {'value': depth0,'optionValuePath': depth0,'optionLabelPath': depth0,'content': depth0,'id': depth0};
  hashTypes = {'value': "ID",'optionValuePath': "STRING",'optionLabelPath': "STRING",'content': "ID",'id': "STRING"};
  data.buffer.push(escapeExpression(helpers.view.call(depth0, "Ember.Select", {hash:{
    'value': ("controllers.application.user.taskd_files.taskd_trust"),
    'optionValuePath': ("content.short"),
    'optionLabelPath': ("content.long"),
    'content': ("taskd_trust_settings"),
    'id': ("id_trust")
  },contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n                        <input type=\"file\" name=\"ca\" id=\"id_ca\">\n                        <p class=\"input-note\">\n                            ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "controllers.application.user.taskd_files.taskd_ca", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n                        </p>\n                    </div>\n                </div>\n                <a href=\"\" class=\"button radius\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "save_taskd", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">Save Settings</a>\n                <a href=\"\" class=\"button radius alert\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "reset_taskd", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">Reset to Default</a>\n            </div>\n        </dd>\n        <dd>\n            <a href=\"#twilio\">Twilio SMS Integration</a>\n            <div id=\"twilio\" class=\"content\">\n                <div class=\"row\">\n                    <div class=\"large-12 columns\">\n                        <label>Twilio Auth Token</label>\n                        ");
  hashContexts = {'type': depth0,'id': depth0,'name': depth0,'value': depth0};
  hashTypes = {'type': "STRING",'id': "STRING",'name': "STRING",'value': "ID"};
  options = {hash:{
    'type': ("text"),
    'id': ("id_twilio_auth_token"),
    'name': ("twilio_auth_token"),
    'value': ("controllers.application.user.twilio_auth_token")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.input || depth0.input),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "input", options))));
  data.buffer.push("\n                    </div>\n                    <div class=\"large-12 columns\">\n                        <label>Phone number whitelist</label>\n                        ");
  hashContexts = {'name': depth0,'id': depth0,'value': depth0,'placeholder': depth0};
  hashTypes = {'name': "STRING",'id': "STRING",'value': "ID",'placeholder': "STRING"};
  options = {hash:{
    'name': ("sms_whitelist"),
    'id': ("id_sms_whitelist"),
    'value': ("controllers.application.user.sms_whitelist"),
    'placeholder': ("+15555555555")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.textarea || depth0.textarea),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "textarea", options))));
  data.buffer.push("\n                        <p class='input-note'>\n                            One phone number per line.  Leave empty to allow messages from any phone number.\n                        </p>\n                    </div>\n                </div>\n                <a href=\"\" class=\"button radius\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "save_twilio", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">Save Settings</a>\n            </div>\n        </dd>\n        <dd>\n            <a href=\"#custom_taskrc\">Custom <span class=\"code\">.taskrc</span></a>\n            <div id=\"custom_taskrc\" class=\"content\">\n                <div class=\"row\">\n                    <div class=\"large-12 columns\">\n                        ");
  hashContexts = {'name': depth0,'value': depth0,'cols': depth0,'rows': depth0};
  hashTypes = {'name': "STRING",'value': "ID",'cols': "STRING",'rows': "STRING"};
  options = {hash:{
    'name': ("custom_taskrc"),
    'value': ("controllers.application.user.taskrc_extras"),
    'cols': ("80"),
    'rows': ("10")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.textarea || depth0.textarea),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "textarea", options))));
  data.buffer.push("\n                        <p class=\"input-note\">\n                            Only configuration values relating to urgency will have an effect,\n                            but entering your entire local <span class=\"code\">.taskrc</span>\n                            is both safe and encouraged.\n                        </p>\n                    </div>\n                </div>\n                <a href=\"\" class=\"button radius\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "save_taskrc", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">Save Settings</a>\n            </div>\n        </dd>\n    </dl>\n</div>\n");
  return buffer;
  
});

this["Ember"]["TEMPLATES"]["create_annotation"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', stack1, hashContexts, hashTypes, options, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;


  data.buffer.push("<div id=\"new_annotation_form\" class=\"reveal-modal\" data-reveal>\n    <div class=\"row\">\n        <div class=\"medium-12 columns\">\n            <h2>Add Annotation</h2>\n        </div>\n    </div>\n    <div class=\"row\">\n        <div class=\"medium-12 columns\">\n            ");
  hashContexts = {'id': depth0};
  hashTypes = {'id': "STRING"};
  options = {hash:{
    'id': ("new_annotation_body")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.textarea || depth0.textarea),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "textarea", options))));
  data.buffer.push("\n        </div>\n    </div>\n    <div class=\"row\">\n        <div class=\"medium-12 columns\">\n            <button class=\"secondary-button\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "save", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">\n                <i class=\"fa fa-save\">Save</i>\n            </button>\n        </div>\n    </div>\n    <a class=\"close-reveal-modal\">&#215;</a>\n</div>\n");
  return buffer;
  
});

this["Ember"]["TEMPLATES"]["create_task"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', stack1, hashTypes, hashContexts, options, self=this, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;

function program1(depth0,data) {
  
  
  data.buffer.push("\n                <h2>Edit task</h2>\n            ");
  }

function program3(depth0,data) {
  
  
  data.buffer.push("\n                <h2>Create a new task</h2>\n            ");
  }

  data.buffer.push("<div id=\"new_task_form\" class=\"reveal-modal\" data-reveal>\n    <div class=\"row\">\n        <div class=\"medium-12 columns\">\n            ");
  hashTypes = {};
  hashContexts = {};
  stack1 = helpers['if'].call(depth0, "uuid", {hash:{},inverse:self.program(3, program3, data),fn:self.program(1, program1, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack1 || stack1 === 0) { data.buffer.push(stack1); }
  data.buffer.push("\n        </div>\n    </div>\n    <div class=\"row\">\n        <div class=\"medium-12 columns\">\n            <label>Description</label>\n            ");
  hashContexts = {'value': depth0};
  hashTypes = {'value': "ID"};
  options = {hash:{
    'value': ("description")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.input || depth0.input),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "input", options))));
  data.buffer.push("\n        </div>\n    </div>\n    <div class=\"row\">\n        <div class=\"medium-4 columns\">\n            <label>Priority</label>\n            ");
  hashContexts = {'content': depth0,'optionValuePath': depth0,'optionLabelPath': depth0,'value': depth0};
  hashTypes = {'content': "ID",'optionValuePath': "STRING",'optionLabelPath': "STRING",'value': "ID"};
  data.buffer.push(escapeExpression(helpers.view.call(depth0, "Ember.Select", {hash:{
    'content': ("priorities"),
    'optionValuePath': ("content.short"),
    'optionLabelPath': ("content.long"),
    'value': ("priority")
  },contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n        </div>\n        <div class=\"medium-4 columns\">\n            <label>Project</label>\n            ");
  hashContexts = {'value': depth0};
  hashTypes = {'value': "ID"};
  options = {hash:{
    'value': ("project")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.input || depth0.input),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "input", options))));
  data.buffer.push("\n        </div>\n        <div class=\"medium-4 columns\">\n            <label>Tags</label>\n            ");
  hashContexts = {'identity': depth0,'tags': depth0,'placeholder': depth0};
  hashTypes = {'identity': "ID",'tags': "ID",'placeholder': "STRING"};
  data.buffer.push(escapeExpression(helpers.view.call(depth0, "App.TagField", {hash:{
    'identity': ("uuid"),
    'tags': ("tags"),
    'placeholder': ("tag1 tag2 (tags separated by a space)")
  },contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n        </div>\n    </div>\n    <div class=\"row\">\n        <div class=\"medium-4 columns\">\n            <label>Due</label>\n            ");
  hashContexts = {'identity': depth0,'date': depth0,'placeholder': depth0};
  hashTypes = {'identity': "ID",'date': "ID",'placeholder': "STRING"};
  data.buffer.push(escapeExpression(helpers.view.call(depth0, "App.DateField", {hash:{
    'identity': ("uuid"),
    'date': ("due"),
    'placeholder': ("YYYY-MM-DD HH:MM")
  },contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n        </div>\n        <div class=\"medium-4 columns\">\n            <label>Wait</label>\n            ");
  hashContexts = {'identity': depth0,'date': depth0,'placeholder': depth0};
  hashTypes = {'identity': "ID",'date': "ID",'placeholder': "STRING"};
  data.buffer.push(escapeExpression(helpers.view.call(depth0, "App.DateField", {hash:{
    'identity': ("uuid"),
    'date': ("wait"),
    'placeholder': ("YYYY-MM-DD HH:MM")
  },contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n        </div>\n        <div class=\"medium-4 columns\">\n            <label>Scheduled</label>\n            ");
  hashContexts = {'identity': depth0,'date': depth0,'placeholder': depth0};
  hashTypes = {'identity': "ID",'date': "ID",'placeholder': "STRING"};
  data.buffer.push(escapeExpression(helpers.view.call(depth0, "App.DateField", {hash:{
    'identity': ("uuid"),
    'date': ("scheduled"),
    'placeholder': ("YYYY-MM-DD HH:MM")
  },contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n        </div>\n    </div>\n\n    <div class=\"row\">\n        <div class=\"medium-12 columns\">\n            <button class=\"secondary-button\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "save", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">\n                <i class=\"fa fa-save\">Save</i>\n            </button>\n        </div>\n    </div>\n\n    <a class=\"close-reveal-modal\">&#215;</a>\n</div>\n");
  return buffer;
  
});

this["Ember"]["TEMPLATES"]["error"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  


  data.buffer.push("<div class=\"row standalone\">\n    <h2>An error was encountered.</h2>\n</div>\n");
  
});

this["Ember"]["TEMPLATES"]["getting_started"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', stack1, stack2, hashTypes, hashContexts, options, self=this, helperMissing=helpers.helperMissing;

function program1(depth0,data) {
  
  
  data.buffer.push("follow the instructions");
  }

  data.buffer.push("<div class=\"row standalone\">\n    <h2>Let's get started</h2>\n    <p>\n        You can \n        ");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},inverse:self.noop,fn:self.program(1, program1, data),contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  stack2 = ((stack1 = helpers['link-to'] || depth0['link-to']),stack1 ? stack1.call(depth0, "configure", options) : helperMissing.call(depth0, "link-to", "configure", options));
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n        for syncing your local\n        taskwarrior client with inthe.am, or you can\n        add tasks directly.\n    </p>\n</div>\n");
  return buffer;
  
});

this["Ember"]["TEMPLATES"]["index"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  


  data.buffer.push("<div class=\"row standalone\">\n</div>\n");
  
});

this["Ember"]["TEMPLATES"]["mobileTasks"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', stack1, hashTypes, hashContexts, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = '', stack1, stack2, hashTypes, hashContexts, options;
  data.buffer.push("\n            <div class=\"task\">\n                ");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},inverse:self.noop,fn:self.program(2, program2, data),contexts:[depth0,depth0],types:["STRING","ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  stack2 = ((stack1 = helpers['link-to'] || depth0['link-to']),stack1 ? stack1.call(depth0, "task", "task", options) : helperMissing.call(depth0, "link-to", "task", "task", options));
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n            </div>\n        ");
  return buffer;
  }
function program2(depth0,data) {
  
  var buffer = '', stack1, stack2, hashContexts, hashTypes, options;
  data.buffer.push("\n                    <div ");
  hashContexts = {'class': depth0};
  hashTypes = {'class': "STRING"};
  options = {hash:{
    'class': (":task-item task.taskwarrior_class")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers['bind-attr'] || depth0['bind-attr']),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "bind-attr", options))));
  data.buffer.push(">\n                        <div ");
  hashContexts = {'class': depth0};
  hashTypes = {'class': "STRING"};
  options = {hash:{
    'class': (":task-list-icon task.status")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers['bind-attr'] || depth0['bind-attr']),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "bind-attr", options))));
  data.buffer.push(">\n                            <i ");
  hashContexts = {'class': depth0};
  hashTypes = {'class': "STRING"};
  options = {hash:{
    'class': (":task-icon :fa task.icon")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers['bind-attr'] || depth0['bind-attr']),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "bind-attr", options))));
  data.buffer.push("></i>\n                        </div>\n                        <div class=\"task-list-item\">\n                            ");
  hashTypes = {};
  hashContexts = {};
  stack2 = helpers['if'].call(depth0, "task.project", {hash:{},inverse:self.noop,fn:self.program(3, program3, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n                            <p class=\"description\">");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "task.description", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</p>\n                            ");
  hashTypes = {};
  hashContexts = {};
  stack2 = helpers.each.call(depth0, "task.tags", {hash:{},inverse:self.noop,fn:self.program(5, program5, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n                        </div>\n                    </div>\n                ");
  return buffer;
  }
function program3(depth0,data) {
  
  var buffer = '', stack1, hashContexts, hashTypes, options;
  data.buffer.push("\n                                <h5 class=\"status\" ");
  hashContexts = {'title': depth0};
  hashTypes = {'title': "STRING"};
  options = {hash:{
    'title': ("task.project")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers['bind-attr'] || depth0['bind-attr']),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "bind-attr", options))));
  data.buffer.push(">");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.propercase || depth0.propercase),stack1 ? stack1.call(depth0, "task.project", options) : helperMissing.call(depth0, "propercase", "task.project", options))));
  data.buffer.push("</h5>\n                            ");
  return buffer;
  }

function program5(depth0,data) {
  
  var buffer = '', hashTypes, hashContexts;
  data.buffer.push("\n                                <i class=\"fa fa-tag\">");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</i>\n                            ");
  return buffer;
  }

function program7(depth0,data) {
  
  
  data.buffer.push("\n            <div class=\"task task-selected pure-g\">\n                Nothing to see here...\n            </div>\n        ");
  }

  data.buffer.push("<div class=\"row full-width\">\n    <div id=\"mobile-list\">\n        ");
  hashTypes = {};
  hashContexts = {};
  stack1 = helpers.each.call(depth0, "task", "in", "pendingTasks", {hash:{},inverse:self.program(7, program7, data),fn:self.program(1, program1, data),contexts:[depth0,depth0,depth0],types:["ID","ID","ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack1 || stack1 === 0) { data.buffer.push(stack1); }
  data.buffer.push("\n    </div>\n</div>\n");
  return buffer;
  
});

this["Ember"]["TEMPLATES"]["sms"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', stack1, hashTypes, hashContexts, escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = '', hashTypes, hashContexts;
  data.buffer.push("\n        <table class=\"pure-table pure-table-horizontal\">\n            <tr>\n                <th>\n                    Twilio Messaging Request URL <strong>(POST)</strong>\n                </th>\n                <td>\n                    https://inthe.am");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "controllers.application.urls.sms_url", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n                </td>\n            </tr>\n        </table>\n    ");
  return buffer;
  }

function program3(depth0,data) {
  
  
  data.buffer.push("\n        <div class=\"block error\">\n            <p>\n                For your security, the ability to send task messages via\n                SMS is currently disabled for your account since you\n                have not yet entered your Twilio auth token.\n            </p>\n            <p>\n                This token is necessary for verifying that incoming messages\n                were sent to Inthe.AM by Twilio from your account.\n            </p>\n        </div>\n    ");
  }

  data.buffer.push("<div class=\"row standalone\">\n    <h2>Adding tasks via SMS</h2>\n\n    ");
  hashTypes = {};
  hashContexts = {};
  stack1 = helpers['if'].call(depth0, "controllers.application.user.twilio_auth_token", {hash:{},inverse:self.program(3, program3, data),fn:self.program(1, program1, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack1 || stack1 === 0) { data.buffer.push(stack1); }
  data.buffer.push("\n\n    <h3>Setup Instructions</h3>\n\n    <p>\n        Inthe.am can receive and add items to your task list via SMS, but\n        it requires a little bit of configuration on your part.\n    </p>\n    <ol>\n        <li>Sign up for a <a href=\"https://www.twilio.com/try-twilio\">Twilio account</a>.</li>\n        <li>\n            Add funds to your twilio account. At the time of writing,  Twilio charges\n            around $0.01 for each incoming or outgoing SMS message (incoming messages are slightly cheaper),\n            and each phone number costs $1.00/month.\n        </li>\n        <li>\n            <a href=\"https://www.twilio.com/user/account/phone-numbers/available/local\">Buy a phone number</a>.\n        </li>\n        <li>\n            From your phone number's configuration screen, set the field \"Messaging Request URL\" to\n            your personal incoming SMS URL: <span class=\"code\">https://inthe.am");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "controllers.application.urls.sms_url", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</span>.\n        </li>\n        <li>\n            Press save.\n        </li>\n    </ol>\n    <p>\n        After you have configured the above, you can send SMS messages to your\n        Twilio phone number.  Currently, the only command implemented is 'add',\n        but in the future additional commands may be added.\n    </p>\n    <p>\n        As an example, you could add a task to the project \"birthday\" with a due\n        date of tomorrow and high priority by sending an SMS message with the following\n        contents:\n        <pre>add project:birthday due:tomorrow priority:h It's my birthday</pre>\n    </p>\n</div>\n");
  return buffer;
  
});

this["Ember"]["TEMPLATES"]["synchronization"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', hashTypes, hashContexts, escapeExpression=this.escapeExpression;


  data.buffer.push("<div class=\"row standalone\">\n    <h2>Synchronizing with Taskwarrior</h2>\n    <table class=\"pure-table pure-table-horizontal\">\n        <tr>\n            <th>\n                Your Certificate\n            </th>\n            <td>\n                <a href=\"");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.unbound.call(depth0, "controllers.application.urls.my_certificate", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\">private.cert.pem</a>\n            </td>\n        </tr>\n        <tr>\n            <th>\n               Your Key \n            </th>\n            <td>\n                <a href=\"");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.unbound.call(depth0, "controllers.application.urls.my_key", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\">private.key.pem</a>\n            </td>\n        </tr>\n        <tr>\n            <th>\n                Authority Certificate\n            </th>\n            <td>\n                <a href=\"");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.unbound.call(depth0, "controllers.application.urls.ca_certificate", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\">ca.cert.pem</a>\n            </td>\n        </tr>\n    </table>\n    \n    <p>\n        Add the following settings to your Taskwarrior configuration file (<code>~/.taskrc</code>).\n    </p>\n\n    <code>\n    <pre>\n        taskd.certificate=/path/to/<a href=\"");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.unbound.call(depth0, "controllers.application.urls.my_certificate", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\">private.cert.pem</a>\n        taskd.key=/path/to/<a href=\"");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.unbound.call(depth0, "controllers.application.urls.my_key", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\">private.key.pem</a>\n        taskd.ca=/path/to/<a href=\"");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.unbound.call(depth0, "controllers.application.urls.ca_certificate", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\">ca.cert.pem</a>\n        taskd.server=");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "controllers.application.user.taskd_server", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n        taskd.credentials=");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "controllers.application.user.taskd_credentials", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n    </pre>\n    </code>\n</div>\n");
  return buffer;
  
});

this["Ember"]["TEMPLATES"]["task"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', stack1, stack2, hashTypes, hashContexts, options, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = '', stack1, hashContexts, hashTypes, options;
  data.buffer.push("\n            <p class=\"subtitle\" ");
  hashContexts = {'title': depth0};
  hashTypes = {'title': "STRING"};
  options = {hash:{
    'title': ("project")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers['bind-attr'] || depth0['bind-attr']),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "bind-attr", options))));
  data.buffer.push(">\n                <span class=\"project\">");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.propercase || depth0.propercase),stack1 ? stack1.call(depth0, "project", options) : helperMissing.call(depth0, "propercase", "project", options))));
  data.buffer.push("</span>\n            </p>\n        ");
  return buffer;
  }

function program3(depth0,data) {
  
  var buffer = '', hashTypes, hashContexts;
  data.buffer.push("\n                <i class=\"fa fa-tag\">");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</i>\n            ");
  return buffer;
  }

function program5(depth0,data) {
  
  var buffer = '', stack1, hashTypes, hashContexts;
  data.buffer.push("\n            <button class=\"secondary-button\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "complete", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">\n                <i class=\"fa fa-check-circle-o\">Mark Completed</i>\n            </button>\n            <button class=\"secondary-button\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "edit", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">\n                <i class=\"fa fa-pencil-square-o\">Edit</i>\n            </button>\n            <button class=\"secondary-button\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "add_annotation", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">\n                <i class=\"fa fa-pencil\">Add Annotation</i>\n            </button>\n            ");
  hashTypes = {};
  hashContexts = {};
  stack1 = helpers['if'].call(depth0, "start", {hash:{},inverse:self.program(8, program8, data),fn:self.program(6, program6, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack1 || stack1 === 0) { data.buffer.push(stack1); }
  data.buffer.push("\n        ");
  return buffer;
  }
function program6(depth0,data) {
  
  var buffer = '', hashTypes, hashContexts;
  data.buffer.push("\n                <button class=\"secondary-button\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "stop", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">\n                    <i class=\"fa fa-star-o\">Stop</i>\n                </button>\n            ");
  return buffer;
  }

function program8(depth0,data) {
  
  var buffer = '', hashTypes, hashContexts;
  data.buffer.push("\n                <button class=\"secondary-button\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "start", {hash:{},contexts:[depth0],types:["STRING"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">\n                    <i class=\"fa fa-star\">Start</i>\n                </button>\n            ");
  return buffer;
  }

function program10(depth0,data) {
  
  var buffer = '', stack1, hashTypes, hashContexts;
  data.buffer.push("\n                    <tr>\n                        <th>Depends Upon</th>\n                        <td>\n                            <ul class=\"depends_tickets\">\n                                ");
  hashTypes = {};
  hashContexts = {};
  stack1 = helpers.each.call(depth0, "dependent_tickets", {hash:{},inverse:self.noop,fn:self.program(11, program11, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack1 || stack1 === 0) { data.buffer.push(stack1); }
  data.buffer.push("\n                            </ul>\n                        </td>\n                    </tr>\n                ");
  return buffer;
  }
function program11(depth0,data) {
  
  var buffer = '', stack1, stack2, hashContexts, hashTypes, options;
  data.buffer.push("\n                                    <li ");
  hashContexts = {'class': depth0};
  hashTypes = {'class': "STRING"};
  options = {hash:{
    'class': ("this.status")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers['bind-attr'] || depth0['bind-attr']),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "bind-attr", options))));
  data.buffer.push(">\n                                        ");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},inverse:self.noop,fn:self.program(12, program12, data),contexts:[depth0,depth0],types:["STRING","ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  stack2 = ((stack1 = helpers['link-to'] || depth0['link-to']),stack1 ? stack1.call(depth0, "task", "", options) : helperMissing.call(depth0, "link-to", "task", "", options));
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n                                    </li>\n                                ");
  return buffer;
  }
function program12(depth0,data) {
  
  var hashTypes, hashContexts;
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "description", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  }

function program14(depth0,data) {
  
  var buffer = '', hashTypes, hashContexts;
  data.buffer.push("\n                            <i class=\"fa fa-tag\">");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</i>\n                        ");
  return buffer;
  }

function program16(depth0,data) {
  
  var buffer = '', stack1, hashTypes, hashContexts, options;
  data.buffer.push("\n                <li>\n                    <a ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "delete_annotation", "description", {hash:{},contexts:[depth0,depth0],types:["STRING","ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">&#215;</a>\n                    ");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.calendar || depth0.calendar),stack1 ? stack1.call(depth0, "entry", options) : helperMissing.call(depth0, "calendar", "entry", options))));
  data.buffer.push(":\n                    ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "description", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n                </li>\n            ");
  return buffer;
  }

  data.buffer.push("<div class=\"row task-content-header\">\n    <div class=\"medium-12 columns\">\n        <h1 class=\"title\">\n            ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "description", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n        </h1>\n        ");
  hashTypes = {};
  hashContexts = {};
  stack1 = helpers['if'].call(depth0, "project", {hash:{},inverse:self.noop,fn:self.program(1, program1, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack1 || stack1 === 0) { data.buffer.push(stack1); }
  data.buffer.push("\n        <div class=\"tags\">\n            ");
  hashTypes = {};
  hashContexts = {};
  stack1 = helpers.each.call(depth0, "tags", {hash:{},inverse:self.noop,fn:self.program(3, program3, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack1 || stack1 === 0) { data.buffer.push(stack1); }
  data.buffer.push("\n        </div>\n    </div>\n</div>\n<div class=\"row\">\n    <div class=\"medium-12 columns\">\n        ");
  hashTypes = {};
  hashContexts = {};
  stack1 = helpers['if'].call(depth0, "editable", {hash:{},inverse:self.noop,fn:self.program(5, program5, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack1 || stack1 === 0) { data.buffer.push(stack1); }
  data.buffer.push("\n    </div>\n</div>\n<div class=\"row task-content-body\">\n    <div class=\"medium-6 columns\">\n        <table class=\"details\">\n            <tbody>\n                ");
  hashTypes = {};
  hashContexts = {};
  stack1 = helpers['if'].call(depth0, "dependent_tickets", {hash:{},inverse:self.noop,fn:self.program(10, program10, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack1 || stack1 === 0) { data.buffer.push(stack1); }
  data.buffer.push("\n                <tr>\n                    <th>Description</th>\n                    <td>");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "description", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</td>\n                </tr>\n                <tr>    \n                    <th>Project</th>\n                    <td><span class=\"project\">");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "project", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</span></td>\n                </tr>\n                <tr>\n                    <th>Status</th>\n                    <td>");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.propercase || depth0.propercase),stack1 ? stack1.call(depth0, "status", options) : helperMissing.call(depth0, "propercase", "status", options))));
  data.buffer.push("</td>\n                </tr>\n                <tr>\n                    <th>Tags</th>\n                    <td>\n                        ");
  hashTypes = {};
  hashContexts = {};
  stack2 = helpers.each.call(depth0, "tags", {hash:{},inverse:self.noop,fn:self.program(14, program14, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n                    </td>\n                </tr>\n                <tr>\n                    <th>Urgency</th>\n                    <td>");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "urgency", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</td>\n                </tr>\n                <tr>\n                    <th>Priority</th>\n                    <td>");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "priority", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</td>\n                </tr>\n                <tr>\n                    <th>Due</th>\n                    <td>");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.calendar || depth0.calendar),stack1 ? stack1.call(depth0, "due", options) : helperMissing.call(depth0, "calendar", "due", options))));
  data.buffer.push("</td>\n                </tr>\n                <tr>\n                    <th>Entered</th>\n                    <td>");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.calendar || depth0.calendar),stack1 ? stack1.call(depth0, "entry", options) : helperMissing.call(depth0, "calendar", "entry", options))));
  data.buffer.push("</td>\n                </tr>\n                <tr>\n                    <th>Started</th>\n                    <td>");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.calendar || depth0.calendar),stack1 ? stack1.call(depth0, "start", options) : helperMissing.call(depth0, "calendar", "start", options))));
  data.buffer.push("</td>\n                </tr>\n                <tr>\n                    <th>Wait</th>\n                    <td>");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.calendar || depth0.calendar),stack1 ? stack1.call(depth0, "wait", options) : helperMissing.call(depth0, "calendar", "wait", options))));
  data.buffer.push("</td>\n                </tr>\n                <tr>\n                    <th>Scheduled</th>\n                    <td>");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.calendar || depth0.calendar),stack1 ? stack1.call(depth0, "scheduled", options) : helperMissing.call(depth0, "calendar", "scheduled", options))));
  data.buffer.push("</td>\n                </tr>\n                <tr>\n                    <th>Modified</th>\n                    <td>");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.calendar || depth0.calendar),stack1 ? stack1.call(depth0, "modified", options) : helperMissing.call(depth0, "calendar", "modified", options))));
  data.buffer.push("</td>\n                </tr>\n                <tr>\n                    <th>UUID</th>\n                    <td><span class=\"uuid\">");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "uuid", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</span></td>\n                </tr>\n            </tbody>\n        </table>\n    </div>\n    <div class=\"medium-6 columns\">\n        <ul class='annotation_list'>\n            ");
  hashTypes = {};
  hashContexts = {};
  stack2 = helpers.each.call(depth0, "processed_annotations", {hash:{},inverse:self.noop,fn:self.program(16, program16, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n        </ul>\n    </div>\n</div>\n");
  return buffer;
  
});

this["Ember"]["TEMPLATES"]["tasks"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', stack1, hashTypes, hashContexts, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = '', stack1, stack2, hashContexts, hashTypes, options;
  data.buffer.push("\n            ");
  hashContexts = {'tagName': depth0,'class': depth0};
  hashTypes = {'tagName': "STRING",'class': "STRING"};
  options = {hash:{
    'tagName': ("div"),
    'class': ("task")
  },inverse:self.noop,fn:self.program(2, program2, data),contexts:[depth0,depth0],types:["STRING","ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  stack2 = ((stack1 = helpers['link-to'] || depth0['link-to']),stack1 ? stack1.call(depth0, "task", "task", options) : helperMissing.call(depth0, "link-to", "task", "task", options));
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n        ");
  return buffer;
  }
function program2(depth0,data) {
  
  var buffer = '', stack1, stack2, hashContexts, hashTypes, options;
  data.buffer.push("\n                <div ");
  hashContexts = {'class': depth0};
  hashTypes = {'class': "STRING"};
  options = {hash:{
    'class': (":task-item task.taskwarrior_class")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers['bind-attr'] || depth0['bind-attr']),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "bind-attr", options))));
  data.buffer.push(">\n                    <div ");
  hashContexts = {'class': depth0};
  hashTypes = {'class': "STRING"};
  options = {hash:{
    'class': (":task-list-icon task.status")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers['bind-attr'] || depth0['bind-attr']),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "bind-attr", options))));
  data.buffer.push(">\n                        <i ");
  hashContexts = {'class': depth0};
  hashTypes = {'class': "STRING"};
  options = {hash:{
    'class': (":task-icon :fa task.icon")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers['bind-attr'] || depth0['bind-attr']),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "bind-attr", options))));
  data.buffer.push("></i>\n                    </div>\n                    <div class=\"task-list-item\">\n                        ");
  hashTypes = {};
  hashContexts = {};
  stack2 = helpers['if'].call(depth0, "task.project", {hash:{},inverse:self.noop,fn:self.program(3, program3, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n                        <p class=\"description\">");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "task.description", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</p>\n                        ");
  hashTypes = {};
  hashContexts = {};
  stack2 = helpers.each.call(depth0, "task.tags", {hash:{},inverse:self.noop,fn:self.program(5, program5, data),contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("\n                    </div>\n                </div>\n            ");
  return buffer;
  }
function program3(depth0,data) {
  
  var buffer = '', stack1, hashContexts, hashTypes, options;
  data.buffer.push("\n                            <h5 class=\"status\" ");
  hashContexts = {'title': depth0};
  hashTypes = {'title': "STRING"};
  options = {hash:{
    'title': ("task.project")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers['bind-attr'] || depth0['bind-attr']),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "bind-attr", options))));
  data.buffer.push(">");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.propercase || depth0.propercase),stack1 ? stack1.call(depth0, "task.project", options) : helperMissing.call(depth0, "propercase", "task.project", options))));
  data.buffer.push("</h5>\n                        ");
  return buffer;
  }

function program5(depth0,data) {
  
  var buffer = '', hashTypes, hashContexts;
  data.buffer.push("\n                            <i class=\"fa fa-tag\">");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</i>\n                        ");
  return buffer;
  }

function program7(depth0,data) {
  
  
  data.buffer.push("\n            <div class=\"task task-selected pure-g\">\n                Nothing to see here...\n            </div>\n        ");
  }

  data.buffer.push("<div class=\"row full-width\">\n    <div id=\"list\">\n        ");
  hashTypes = {};
  hashContexts = {};
  stack1 = helpers.each.call(depth0, "task", "in", "pendingTasks", {hash:{},inverse:self.program(7, program7, data),fn:self.program(1, program1, data),contexts:[depth0,depth0,depth0],types:["ID","ID","ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack1 || stack1 === 0) { data.buffer.push(stack1); }
  data.buffer.push("\n    </div>\n    <div id=\"task-details\">\n        ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "outlet", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n    </div>\n</div>\n");
  return buffer;
  
});

this["Ember"]["TEMPLATES"]["tasksindex"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', stack1, hashTypes, hashContexts, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing, self=this;

function program1(depth0,data) {
  
  var buffer = '', stack1, hashTypes, hashContexts, options;
  data.buffer.push("\n        <div class=\"task pure-g\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "view_task", "task", {hash:{},contexts:[depth0,depth0],types:["STRING","ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">\n            <div ");
  hashContexts = {'class': depth0};
  hashTypes = {'class': "STRING"};
  options = {hash:{
    'class': (":pure-u task.status")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers['bind-attr'] || depth0['bind-attr']),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "bind-attr", options))));
  data.buffer.push(">\n                <i ");
  hashContexts = {'class': depth0};
  hashTypes = {'class': "STRING"};
  options = {hash:{
    'class': (":task-icon :fa task.icon")
  },contexts:[],types:[],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers['bind-attr'] || depth0['bind-attr']),stack1 ? stack1.call(depth0, options) : helperMissing.call(depth0, "bind-attr", options))));
  data.buffer.push("></i>\n            </div>\n            <div class=\"pure-u-3-4\">\n                <h5 class=\"status\">");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "task.status", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</h5>\n                <p class=\"description\">");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "task.description", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("</p>\n            </div>\n        </div>\n    ");
  return buffer;
  }

function program3(depth0,data) {
  
  
  data.buffer.push("\n        <div class=\"task task-selected pure-g\">\n            Nothing to see here...\n        </div>\n    ");
  }

  data.buffer.push("<div class=\"pure-u-1\" id=\"list\">\n    ");
  hashTypes = {};
  hashContexts = {};
  stack1 = helpers.each.call(depth0, "task", "in", "controller", {hash:{},inverse:self.program(3, program3, data),fn:self.program(1, program1, data),contexts:[depth0,depth0,depth0],types:["ID","ID","ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data});
  if(stack1 || stack1 === 0) { data.buffer.push(stack1); }
  data.buffer.push("\n</div>\n<div class=\"pure-u-1\" id=\"main\">\n    <div class=\"task-content\">\n        ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "outlet", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\n    </div>\n</div>\n");
  return buffer;
  
});

this["Ember"]["TEMPLATES"]["unconfigurable"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  


  data.buffer.push("<div class=\"pure-u-1 standalone\">\n    <p>\n        Unfortunately, we weren't able to find any taskwarrior folders in your\n        dropbox account.\n    </p>\n</div>\n");
  
});