(function () {
  if (window.__dc) return;
  window.__dc = { instances: {}, counter: 0 };

  window.DCLogic = function () {
    this.props = {};
    this.state = {};
    this._refs = {};
  };

  DCLogic.prototype.setState = function (updater) {
    var self = this;
    if (typeof updater === 'function') {
      var prev = Object.assign({}, this.state);
      var next = updater(prev);
      for (var k in next) {
        if (next.hasOwnProperty(k)) {
          self.state[k] = next[k];
        }
      }
    } else if (updater && typeof updater === 'object') {
      for (var k in updater) {
        if (updater.hasOwnProperty(k)) {
          self.state[k] = updater[k];
        }
      }
    }
    self._render();
  };

  DCLogic.prototype.renderVals = function () { return {}; };
  DCLogic.prototype.componentDidMount = function () {};

  DCLogic.prototype._init = function (el, template) {
    this._el = el;
    this._rawTemplate = template;
    this._instanceId = ++__dc.counter;
    __dc.instances[this._instanceId] = this;
    el.setAttribute('data-dc-instance', this._instanceId);
    this._wireEvents();
    if (typeof this.componentDidMount === 'function') {
      this.componentDidMount();
    }
    this._render();
  };

  DCLogic.prototype._wireEvents = function () {
    var self = this;
    var events = ['click', 'change', 'mousemove', 'touchstart', 'input'];
    this._handler = function (e) {
      var el = e.target;
      while (el && el !== self._el) {
        var fnName = el.getAttribute('data-dc-event');
        if (fnName && typeof self[fnName] === 'function') {
          self[fnName](e);
          return;
        }
        el = el.parentNode;
      }
    };
    for (var i = 0; i < events.length; i++) {
      this._el.addEventListener(events[i], this._handler);
    }
  };

  DCLogic.prototype._resolve = function (path, ctx) {
    var parts = path.split('.');
    var cur = ctx;
    for (var i = 0; i < parts.length; i++) {
      if (cur == null) return undefined;
      cur = cur[parts[i]];
    }
    return cur;
  };

  DCLogic.prototype._processTemplate = function (html) {
    var self = this;
    var vals = this.renderVals();
    var id = this._instanceId;

    // Process sc-for
    html = html.replace(/<sc-for\s+list="\{\{(.+?)\}\}"\s+as="(.+?)"(.*?)>([\s\S]*?)<\/sc-for>/g, function (match, listExpr, itemName, attrs, content) {
      var list = self._resolve(listExpr.trim(), vals);
      if (!Array.isArray(list)) return '';
      var result = '';
      for (var i = 0; i < list.length; i++) {
        var item = list[i];
        var itemCtx = {};
        itemCtx[itemName] = item;
        var ctx = Object.assign({}, vals, itemCtx);
        result += self._replaceMustaches(content, ctx, id);
      }
      return result;
    });

    // Process sc-if with nesting
    var result = '';
    var remaining = html;
    while (remaining.length > 0) {
      var m = remaining.match(/<sc-if\s+value="\{\{(.+?)\}\}"(.*?)>/);
      if (!m) { result += remaining; break; }
      result += remaining.substring(0, m.index);
      var cond = self._resolve(m[1].trim(), vals);

      var depth = 1;
      var pos = m.index + m[0].length;
      var end = -1;
      while (depth > 0 && pos < remaining.length) {
        var nextOpen = remaining.indexOf('<sc-if ', pos);
        var nextClose = remaining.indexOf('</sc-if>', pos);
        if (nextClose === -1) { end = remaining.length; break; }
        if (nextOpen !== -1 && nextOpen < nextClose) {
          depth++; pos = nextOpen + 7;
        } else {
          depth--;
          if (depth === 0) { end = nextClose; }
          else { pos = nextClose + 8; }
        }
      }
      if (cond) {
        result += self._replaceMustaches(remaining.substring(m.index + m[0].length, end), vals, id);
      }
      remaining = remaining.substring(end + 8);
    }
    html = result;

    // Replace remaining {{ }}
    html = self._replaceMustaches(html, vals, id);

    return html;
  };

  DCLogic.prototype._replaceMustaches = function (html, ctx, id) {
    var self = this;

    // style-hover
    html = html.replace(/\s+style-hover="([^"]*)"/g, function (match, css) {
      return ' style="' + css + '"';
    });

    // onClick -> data-dc-event
    html = html.replace(/\s+(onClick|onChange|onMouseMove|onTouchStart|onInput)="\{\{(.+?)\}\}"/g, function (match, eventAttr, fnName) {
      return ' data-dc-event="' + fnName.trim() + '"';
    });

    // ref
    html = html.replace(/\s+ref="\{\{(.+?)\}\}"/g, function (match, refName) {
      return ' data-dc-ref="' + refName.trim() + '"';
    });

    // general {{ }}
    html = html.replace(/\{\{(.+?)\}\}/g, function (match, expr) {
      var value = self._resolve(expr.trim(), ctx);
      if (value === null || value === undefined) return '';
      if (typeof value === 'function') return '';
      if (typeof value === 'object') return JSON.stringify(value);
      return String(value);
    });

    return html;
  };

  DCLogic.prototype._render = function () {
    var processed = this._processTemplate(this._rawTemplate);
    this._el.innerHTML = processed;

    // Wire refs
    var refs = this._el.querySelectorAll('[data-dc-ref]');
    for (var i = 0; i < refs.length; i++) {
      var el = refs[i];
      var name = el.getAttribute('data-dc-ref');
      if (this[name] && typeof this[name] === 'object' && 'current' in this[name]) {
        this[name].current = el;
      } else {
        this[name] = { current: el };
      }
    }
  };

  // Init
  function init() {
    var xdcs = document.querySelectorAll('x-dc');
    xdcs.forEach(function (xdc) {
      var script = xdc.nextElementSibling;
      if (!script || !script.hasAttribute('data-dc-script')) return;

      var props = {};
      try { props = JSON.parse(script.getAttribute('data-props') || '{}'); } catch (e) {}

      var propDefaults = {};
      for (var key in props) {
        if (props.hasOwnProperty(key) && props[key] && props[key].default !== undefined) {
          propDefaults[key] = props[key].default;
        }
      }

      var serverData = (typeof window !== 'undefined' && window.__APP_DATA__) || {};
      propDefaults = Object.assign({}, propDefaults, serverData);

      var template = xdc.innerHTML;

      // Helmet
      var helmet = template.match(/<helmet>([\s\S]*?)<\/helmet>/);
      if (helmet) {
        var div = document.createElement('div');
        div.innerHTML = helmet[1];
        while (div.firstChild) {
          document.head.appendChild(div.firstChild);
        }
        template = template.replace(/<helmet>[\s\S]*?<\/helmet>/, '');
      }

      var code = script.textContent;
      try {
        var fn = new Function('DCLogic', 'React', code + '\nreturn Component;');
        var ComponentClass = fn(DCLogic, window.React || {});
        var instance = new ComponentClass();
        instance.props = propDefaults;
        instance._init(xdc, template);
        xdc._dcInstance = instance;
      } catch (e) {
        console.error('DC error:', e);
        xdc.innerHTML = '<div style="color:red;padding:20px;">Error: ' + e.message + '</div>';
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
