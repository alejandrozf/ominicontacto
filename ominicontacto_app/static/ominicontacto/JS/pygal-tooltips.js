(function() {
  var $, get_translation, init, init_svg, matches, padding, r_translation, sibl, svg_ns, tooltip_timeout, xlink_ns;

  svg_ns = 'http://www.w3.org/2000/svg';

  xlink_ns = 'http://www.w3.org/1999/xlink';

  $ = function(sel, ctx) {
    if (ctx == null) {
      ctx = null;
    }
    ctx = ctx || document;
    return Array.prototype.slice.call(ctx.querySelectorAll(sel), 0).filter(function(e) {
      return e !== ctx;
    });
  };

  matches = function(el, selector) {
    return (el.matches || el.matchesSelector || el.msMatchesSelector || el.mozMatchesSelector || el.webkitMatchesSelector || el.oMatchesSelector).call(el, selector);
  };

  sibl = function(el, match) {
    if (match == null) {
      match = null;
    }
    return Array.prototype.filter.call(el.parentElement.children, function(child) {
      return child !== el && (!match || matches(child, match));
    });
  };

  Array.prototype.one = function() {
    return this.length > 0 && this[0] || {};
  };

  padding = 5;

  tooltip_timeout = null;

  r_translation = /translate\((\d+)[ ,]+(\d+)\)/;

  get_translation = function(el) {
    return (r_translation.exec(el.getAttribute('transform')) || []).slice(1).map(function(x) {
      return +x;
    });
  };

  init = function(ctx) {
    var bbox, box, config, el, graph, inner_svg, num, parent, tooltip, tooltip_el, tt, uid, untooltip, xconvert, yconvert, _i, _j, _k, _len, _len1, _len2, _ref, _ref1, _ref2, _ref3;
    if ($('svg', ctx).length) {
      inner_svg = $('svg', ctx).one();
      parent = inner_svg.parentElement;
      box = inner_svg.viewBox.baseVal;
      bbox = parent.getBBox();
      xconvert = function(x) {
        return ((x - box.x) / box.width) * bbox.width;
      };
      yconvert = function(y) {
        return ((y - box.y) / box.height) * bbox.height;
      };
    } else {
      xconvert = yconvert = function(x) {
        return x;
      };
    }
    if (((_ref = window.pygal) != null ? _ref.config : void 0) != null) {
      if (window.pygal.config.no_prefix != null) {
        config = window.pygal.config;
      } else {
        uid = ctx.id.replace('chart-', '');
        config = window.pygal.config[uid];
      }
    } else {
      config = window.config;
    }
    tooltip_el = null;
    graph = $('.graph').one();
    tt = $('.tooltip', ctx).one();
    _ref1 = $('.reactive', ctx);
    for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
      el = _ref1[_i];
      el.addEventListener('mouseenter', (function(el) {
        return function() {
          return el.classList.add('active');
        };
      })(el));
      el.addEventListener('mouseleave', (function(el) {
        return function() {
          return el.classList.remove('active');
        };
      })(el));
    }
    _ref2 = $('.activate-serie', ctx);
    for (_j = 0, _len1 = _ref2.length; _j < _len1; _j++) {
      el = _ref2[_j];
      num = el.id.replace('activate-serie-', '');
      el.addEventListener('mouseenter', (function(num) {
        return function() {
          var re, _k, _l, _len2, _len3, _ref3, _ref4, _results;
          _ref3 = $('.serie-' + num + ' .reactive', ctx);
          for (_k = 0, _len2 = _ref3.length; _k < _len2; _k++) {
            re = _ref3[_k];
            re.classList.add('active');
          }
          _ref4 = $('.serie-' + num + ' .showable', ctx);
          _results = [];
          for (_l = 0, _len3 = _ref4.length; _l < _len3; _l++) {
            re = _ref4[_l];
            _results.push(re.classList.add('shown'));
          }
          return _results;
        };
      })(num));
      el.addEventListener('mouseleave', (function(num) {
        return function() {
          var re, _k, _l, _len2, _len3, _ref3, _ref4, _results;
          _ref3 = $('.serie-' + num + ' .reactive', ctx);
          for (_k = 0, _len2 = _ref3.length; _k < _len2; _k++) {
            re = _ref3[_k];
            re.classList.remove('active');
          }
          _ref4 = $('.serie-' + num + ' .showable', ctx);
          _results = [];
          for (_l = 0, _len3 = _ref4.length; _l < _len3; _l++) {
            re = _ref4[_l];
            _results.push(re.classList.remove('shown'));
          }
          return _results;
        };
      })(num));
      el.addEventListener('click', (function(el, num) {
        return function() {
          var ov, re, rect, show, _k, _l, _len2, _len3, _ref3, _ref4, _results;
          rect = $('rect', el).one();
          show = rect.style.fill !== '';
          rect.style.fill = show ? '' : 'transparent';
          _ref3 = $('.serie-' + num + ' .reactive', ctx);
          for (_k = 0, _len2 = _ref3.length; _k < _len2; _k++) {
            re = _ref3[_k];
            re.style.display = show ? '' : 'none';
          }
          _ref4 = $('.text-overlay .serie-' + num, ctx);
          _results = [];
          for (_l = 0, _len3 = _ref4.length; _l < _len3; _l++) {
            ov = _ref4[_l];
            _results.push(ov.style.display = show ? '' : 'none');
          }
          return _results;
        };
      })(el, num));
    }
    _ref3 = $('.tooltip-trigger', ctx);
    for (_k = 0, _len2 = _ref3.length; _k < _len2; _k++) {
      el = _ref3[_k];
      el.addEventListener('mouseenter', (function(el) {
        return function() {
          return tooltip_el = tooltip(el);
        };
      })(el));
    }
    tt.addEventListener('mouseenter', function() {
      return tooltip_el != null ? tooltip_el.classList.add('active') : void 0;
    });
    tt.addEventListener('mouseleave', function() {
      return tooltip_el != null ? tooltip_el.classList.remove('active') : void 0;
    });
    ctx.addEventListener('mouseleave', function() {
      if (tooltip_timeout) {
        clearTimeout(tooltip_timeout);
      }
      return untooltip(0);
    });
    graph.addEventListener('mousemove', function(el) {
      if (tooltip_timeout) {
        return;
      }
      if (!matches(el.target, '.background')) {
        return;
      }
      return untooltip(1000);
    });
    tooltip = function(el) {
      var a, baseline, cls, current_x, current_y, dy, h, i, key, keys, label, legend, name, plot_x, plot_y, rect, serie_index, subval, text, text_group, texts, traversal, value, w, x, x_elt, x_label, xlink, y, y_elt, _l, _len3, _len4, _len5, _m, _n, _ref4, _ref5, _ref6, _ref7, _ref8;
      clearTimeout(tooltip_timeout);
      tooltip_timeout = null;
      tt.style.opacity = 1;
      tt.style.display = '';
      text_group = $('g.text', tt).one();
      rect = $('rect', tt).one();
      text_group.innerHTML = '';
      label = sibl(el, '.label').one().textContent;
      x_label = sibl(el, '.x_label').one().textContent;
      value = sibl(el, '.value').one().textContent;
      xlink = sibl(el, '.xlink').one().textContent;
      serie_index = null;
      parent = el;
      traversal = [];
      while (parent) {
        traversal.push(parent);
        if (parent.classList.contains('series')) {
          break;
        }
        parent = parent.parentElement;
      }
      if (parent) {
        _ref4 = parent.classList;
        for (_l = 0, _len3 = _ref4.length; _l < _len3; _l++) {
          cls = _ref4[_l];
          if (cls.indexOf('serie-') === 0) {
            serie_index = +cls.replace('serie-', '');
            break;
          }
        }
      }
      legend = null;
      if (serie_index !== null) {
        legend = config.legends[serie_index];
      }
      dy = 0;
      keys = [[label, 'label']];
      _ref5 = value.split('\n');
      for (i = _m = 0, _len4 = _ref5.length; _m < _len4; i = ++_m) {
        subval = _ref5[i];
        keys.push([subval, 'value-' + i]);
      }
      if (config.tooltip_fancy_mode) {
        keys.push([xlink, 'xlink']);
        keys.unshift([x_label, 'x_label']);
        keys.unshift([legend, 'legend']);
      }
      texts = {};
      for (_n = 0, _len5 = keys.length; _n < _len5; _n++) {
        _ref6 = keys[_n], key = _ref6[0], name = _ref6[1];
        if (key) {
          text = document.createElementNS(svg_ns, 'text');
          text.textContent = key;
          text.setAttribute('x', padding);
          text.setAttribute('dy', dy);
          text.classList.add(name.indexOf('value') === 0 ? 'value' : name);
          if (name.indexOf('value') === 0 && config.tooltip_fancy_mode) {
            text.classList.add('color-' + serie_index);
          }
          if (name === 'xlink') {
            a = document.createElementNS(svg_ns, 'a');
            a.setAttributeNS(xlink_ns, 'href', key);
            a.textContent = void 0;
            a.appendChild(text);
            text.textContent = 'Link >';
            text_group.appendChild(a);
          } else {
            text_group.appendChild(text);
          }
          dy += text.getBBox().height + padding / 2;
          baseline = padding;
          if (text.style.dominantBaseline !== void 0) {
            text.style.dominantBaseline = 'text-before-edge';
          } else {
            baseline += text.getBBox().height * .8;
          }
          text.setAttribute('y', baseline);
          texts[name] = text;
        }
      }
      w = text_group.getBBox().width + 2 * padding;
      h = text_group.getBBox().height + 2 * padding;
      rect.setAttribute('width', w);
      rect.setAttribute('height', h);
      if (texts.value) {
        texts.value.setAttribute('dx', (w - texts.value.getBBox().width) / 2 - padding);
      }
      if (texts.x_label) {
        texts.x_label.setAttribute('dx', w - texts.x_label.getBBox().width - 2 * padding);
      }
      if (texts.xlink) {
        texts.xlink.setAttribute('dx', w - texts.xlink.getBBox().width - 2 * padding);
      }
      x_elt = sibl(el, '.x').one();
      y_elt = sibl(el, '.y').one();
      x = parseInt(x_elt.textContent);
      if (x_elt.classList.contains('centered')) {
        x -= w / 2;
      } else if (x_elt.classList.contains('left')) {
        x -= w;
      } else if (x_elt.classList.contains('auto')) {
        x = xconvert(el.getBBox().x + el.getBBox().width / 2) - w / 2;
      }
      y = parseInt(y_elt.textContent);
      if (y_elt.classList.contains('centered')) {
        y -= h / 2;
      } else if (y_elt.classList.contains('top')) {
        y -= h;
      } else if (y_elt.classList.contains('auto')) {
        y = yconvert(el.getBBox().y + el.getBBox().height / 2) - h / 2;
      }
      _ref7 = get_translation(tt.parentElement), plot_x = _ref7[0], plot_y = _ref7[1];
      if (x + w + plot_x > config.width) {
        x = config.width - w - plot_x;
      }
      if (y + h + plot_y > config.height) {
        y = config.height - h - plot_y;
      }
      if (x + plot_x < 0) {
        x = -plot_x;
      }
      if (y + plot_y < 0) {
        y = -plot_y;
      }
      _ref8 = get_translation(tt), current_x = _ref8[0], current_y = _ref8[1];
      if (current_x === x && current_y === y) {
        return el;
      }
      tt.setAttribute('transform', "translate(" + x + " " + y + ")");
      return el;
    };
    return untooltip = function(ms) {
      return tooltip_timeout = setTimeout(function() {
        tt.style.display = 'none';
        tt.style.opacity = 0;
        if (tooltip_el != null) {
          tooltip_el.classList.remove('active');
        }
        return tooltip_timeout = null;
      }, ms);
    };
  };

  init_svg = function() {
    var chart, charts, _i, _len, _results;
    charts = $('.pygal-chart');
    if (charts.length) {
      _results = [];
      for (_i = 0, _len = charts.length; _i < _len; _i++) {
        chart = charts[_i];
        _results.push(init(chart));
      }
      return _results;
    }
  };

  if (document.readyState !== 'loading') {
    init_svg();
  } else {
    document.addEventListener('DOMContentLoaded', function() {
      return init_svg();
    });
  }

  window.pygal = window.pygal || {};

  window.pygal.init = init;

  window.pygal.init_svg = init_svg;

}).call(this);
