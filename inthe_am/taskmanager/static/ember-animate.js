(function () {

	var run = function (fn) {
		if (fn && typeof fn === 'function') {
			return fn();
		}
	};

	Ember.View.reopen({

		isAnimatingIn : false,
		isAnimatingOut : false,

		_afterRender : function () {
			var self = this;
			self.willAnimateIn();
			self.set('isAnimatingIn', true);
			self.animateIn(function () {
				self.set('isAnimatingIn', false);
				self.didAnimateIn();
			});
		},

		didInsertElement : function () {
			Ember.run.schedule('afterRender', this, this._afterRender);
			return this._super();
		},

		willAnimateIn : Ember.K,
		willAnimateOut : Ember.K,
		didAnimateIn : Ember.K,
		didAnimateOut : Ember.K,

		animateIn : function (done) {
			run(done);
		},

		animateOut : function (done) {
			run(done);
		},

		destroy : function (done) {

			var self = this,
				_super = Ember.$.proxy(this._super, this);

			self.willAnimateOut();
			self.set('isAnimatingOut', true);
			self.animateOut(function () {
				self.set('isAnimatingOut', false);
				self.didAnimateOut();
				run(done);
				_super();
			});

			return this;
		}
	});

	Ember.ContainerView.reopen({

		currentView : null,
		activeView : null,
		newView : null,

		init : function () {

			var currentView;

			this._super();

			if (currentView = this.get("currentView")) {
				this.set("activeView", currentView);
			}
		},

		_currentViewWillChange : Ember.K,

		_currentViewDidChange : Ember.observer('currentView', function () {

			var self,
				newView,
				oldView,
				removeOldView;

			self = this;
			oldView = this.get('activeView');
			newView = this.get('currentView');

			this.set('newView', newView);

			removeOldView = function () {

				if (oldView.get('isAnimatingOut')) {
					return;
				}

				if (oldView.get('isAnimatingIn')) {
					oldView.addObserver('isAnimatingIn', self, '_currentViewDidChange');
					return;
				}

				oldView.removeObserver('isAnimatingIn', self, '_currentViewDidChange');
				oldView.destroy(function () {
					self._pushNewView.apply(self);
				});
			};

			if (oldView) {
				return removeOldView();
			}

			this._pushNewView();
		}),

		_pushNewView : function () {

			var newView = this.get('newView');

			if (newView) {
				this.pushObject(newView);
			}

			this.set("activeView", newView);
		}
	});

})();