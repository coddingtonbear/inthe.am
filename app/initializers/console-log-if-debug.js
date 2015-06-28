
export default {
    name: 'console-log-if-debug',
    initialize: function(container, application) {
        console.logIfDebug = function(...messages) {
            if(window.localStorage && window.localStorage.getItem('DEBUG')) {
                console.log.apply(console, messages);
            }
        };
    }
};
